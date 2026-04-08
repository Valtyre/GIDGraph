import logging
import os
import re
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

CANONICAL_RELATION_PATTERNS = (
    re.compile(r"^[A-Za-z][A-Za-z0-9/-]* activates [A-Za-z][A-Za-z0-9/-]*\.$"),
    re.compile(r"^[A-Za-z][A-Za-z0-9/-]* inhibits [A-Za-z][A-Za-z0-9/-]*\.$"),
    re.compile(r"^[A-Za-z][A-Za-z0-9/-]* binds [A-Za-z][A-Za-z0-9/-]*\.$"),
    re.compile(r"^[A-Za-z][A-Za-z0-9/-]* knockout inhibits [A-Za-z][A-Za-z0-9/-]*\.$"),
    re.compile(r"^[A-Za-z][A-Za-z0-9/-]* knockout leads to [A-Za-z][A-Za-z0-9/-]*\.$"),
)
EXPLANATION_MARKERS = (
    "here is",
    "here are",
    "explanation",
    "summary",
    "rewritten",
    "optimized text",
    "output:",
    "input:",
)
ACTIVATION_VERBS = (
    "activates",
    "activate",
    "enhances",
    "enhance",
    "induces",
    "induce",
    "promotes",
    "promote",
    "upregulates",
    "upregulate",
    "increases",
    "increase",
)
INHIBITION_VERBS = (
    "inhibits",
    "inhibit",
    "represses",
    "repress",
    "reduces",
    "reduce",
    "decreases",
    "decrease",
    "suppresses",
    "suppress",
    "downregulates",
    "downregulate",
)
RELATION_VERBS = ("activates", "inhibits", "binds", "leads to")
TRAILING_CONTEXT_TOKENS = {
    "cm",
    "cms",
    "cell",
    "cells",
    "ventricle",
    "ventricles",
    "ventricular",
    "atrial",
    "cardiac",
    "derived",
    "human",
    "induced",
    "pluripotent",
    "stem",
    "mice",
    "mouse",
    "in",
    "of",
    "the",
    "a",
    "an",
}

SYSTEM_PROMPT = """You convert biological prose into short parser-friendly relation statements.
Rules:
- Keep only explicit gene-gene or gene-expression relations supported by the app.
- Split multi-relation sentences into separate sentences.
- Output one relation per sentence when possible.
- Use only these relation verbs when possible: activates, inhibits, binds.
- Use "X knockout inhibits Y" when the text says Y expression is lost/reduced in X knockout or X mutant conditions.
- Do not explain.
- Do not summarize.
- Do not include bullets.
- Output plain sentences only.
- Preserve every explicit relation you can infer directly from the text.
- If a relation is ambiguous, omit it rather than guessing."""

USER_PROMPT_TEMPLATE = """Rewrite the following biological text into short parser-friendly statements.
Preserve every explicit supported relation. You may output multiple relations in one sentence if needed, but prefer simple sentences and do not omit explicit relations just to simplify.

Text:
{text}
"""


@dataclass(frozen=True)
class OptimizationResult:
    text: str
    optimized: bool
    fallback: bool


def optimize_text(text: str) -> OptimizationResult:
    cleaned_input = text.strip()
    if not cleaned_input:
        return OptimizationResult(text=text, optimized=False, fallback=False)

    provider = os.getenv("LOCAL_LLM_PROVIDER", "ollama").strip().lower()
    if provider != "ollama":
        _log_rejection(cleaned_input, "", "", "unsupported provider")
        return OptimizationResult(text=text, optimized=False, fallback=True)

    model = os.getenv("OLLAMA_MODEL", "").strip()
    if not model:
        _log_rejection(cleaned_input, "", "", "missing Ollama model")
        return OptimizationResult(text=text, optimized=False, fallback=True)

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "20"))

    try:
        raw_output = _request_ollama(base_url=base_url, model=model, text=cleaned_input, timeout=timeout)
    except (httpx.HTTPError, ValueError) as exc:
        _log_rejection(cleaned_input, "", "", f"Ollama request failed: {exc}")
        return OptimizationResult(text=text, optimized=False, fallback=True)

    sanitized_output = _sanitize_output(raw_output)
    kept_sentences, dropped_reasons = _extract_valid_sentences(sanitized_output)

    if not kept_sentences:
        _log_rejection(
            cleaned_input,
            raw_output,
            sanitized_output,
            "no valid relation sentences remained after normalization",
        )
        return OptimizationResult(text=text, optimized=False, fallback=True)

    if dropped_reasons:
        _log_rejection(
            cleaned_input,
            raw_output,
            sanitized_output,
            "; ".join(dropped_reasons),
        )

    return OptimizationResult(text=" ".join(kept_sentences), optimized=True, fallback=False)


def _request_ollama(base_url: str, model: str, text: str, timeout: float) -> str:
    response = httpx.post(
        f"{base_url}/api/chat",
        json={
            "model": model,
            "stream": False,
            "options": {
                "temperature": 0,
                "top_p": 1,
            },
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=text)},
            ],
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["message"]["content"]


def _sanitize_output(output: str) -> str:
    text = output.strip()
    text = re.sub(r"```(?:text)?", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")
    text = re.sub(r"(^|\s)([-*•]|\d+\.)\s+", r"\1", text)
    text = re.sub(r"([a-z)])\.([A-Z])", r"\1. \2", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+\.", ".", text)
    return text


def _extract_valid_sentences(text: str) -> tuple[list[str], list[str]]:
    kept: list[str] = []
    dropped: list[str] = []

    for sentence in _split_candidate_sentences(text):
        normalized_sentences, reason = _normalize_sentence(sentence)
        if normalized_sentences:
            for normalized in normalized_sentences:
                if _is_valid_sentence(normalized) and normalized not in kept:
                    kept.append(normalized)
        elif reason:
            dropped.append(f"dropped sentence: {reason}: {sentence.strip()}")

    return kept, dropped


def _split_candidate_sentences(text: str) -> list[str]:
    if not text:
        return []
    return [sentence.strip() for sentence in re.split(r"(?<=\.)\s+", text) if sentence.strip()]


def _normalize_sentence(sentence: str) -> tuple[list[str], str | None]:
    cleaned = sentence.strip()
    if not cleaned:
        return [], None

    lowered = cleaned.lower()
    if any(marker in lowered for marker in EXPLANATION_MARKERS):
        return [], "explanatory text"

    cleaned = cleaned.rstrip(".").strip()
    cleaned = _strip_context_prefix(cleaned)
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    cleaned = re.sub(r"\bexpression of\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bgene expression\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bexpression\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bgene\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bdirectly\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\balso\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bboth\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r",", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;:")

    knockout_relations = _normalize_knockout_sentence(cleaned)
    if knockout_relations:
        return knockout_relations, None

    cleaned = re.sub(r"\bbinds to genomic loci of\b", "binds", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bbinds promoter of\b", "binds", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bbinds to\b", "binds", cleaned, flags=re.IGNORECASE)

    for verb in ACTIVATION_VERBS:
        cleaned = re.sub(rf"\b{re.escape(verb)}\b", "activates", cleaned, flags=re.IGNORECASE)
    for verb in INHIBITION_VERBS:
        cleaned = re.sub(rf"\b{re.escape(verb)}\b", "inhibits", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;:")

    relation_match = re.match(
        r"^(.+?)\s+(activates|inhibits|binds|leads to)\s+(.+)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if not relation_match:
        return [], "no supported relation verb after normalization"

    source_text, relation, target_text = relation_match.groups()
    sources = _expand_gene_list(source_text)

    if not sources:
        return [], "unsupported multi-gene structure in source"

    self_relation_targets = _normalize_self_relation_targets(target_text, relation, sources)
    if self_relation_targets:
        return self_relation_targets, None

    targets = _expand_gene_list(target_text)
    if not targets:
        return [], "ambiguous non-gene target"

    sentences = [
        f"{source} {relation.lower()} {target}."
        for source in sources
        for target in targets
    ]
    return sentences, None


def _normalize_self_relation_targets(target_text: str, relation: str, sources: list[str]) -> list[str]:
    lowered_target = target_text.strip().lower().rstrip(".")
    self_patterns = (
        "itself",
        "its own expression",
        "its own promoter",
    )

    if lowered_target not in self_patterns:
        return []

    return [f"{source} {relation.lower()} {source}." for source in sources]


def _normalize_knockout_sentence(cleaned: str) -> list[str]:
    source_pattern = r"([A-Za-z][A-Za-z0-9/-]*)"
    knockout_patterns = [
        rf"^([A-Za-z][A-Za-z0-9/-]*)\s+is\s+(?:lost|absent|reduced|decreased)\s+by\s+{source_pattern}(?:\s+(?:knockout|mutant))(?:\b.*)?$",
        rf"^([A-Za-z][A-Za-z0-9/-]*)\s+is\s+(?:lost|absent|reduced|decreased)\s+in\s+{source_pattern}(?:\s+(?:knockout|mutant))(?:\b.*)?$",
    ]

    for pattern in knockout_patterns:
        match = re.match(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            target, source = match.groups()
            return [f"{source} knockout inhibits {target}."]

    knockout_relation_match = re.match(
        r"^([A-Za-z][A-Za-z0-9/-]*)\s+knockout\s+(inhibits|leads to)\s+([A-Za-z][A-Za-z0-9/-]*)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if knockout_relation_match:
        source, relation, target = knockout_relation_match.groups()
        return [f"{source} knockout {relation.lower()} {target}."]

    return []


def _expand_gene_list(text: str) -> list[str]:
    cleaned = text.strip()
    cleaned = re.sub(r"^(?:the\s+)?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip(" ,;:")
    if not cleaned:
        return []

    parts = re.split(r"\s+(?:and|or)\s+", cleaned, flags=re.IGNORECASE)
    genes: list[str] = []
    for part in parts:
        gene = _extract_gene_token(part)
        if gene and gene not in genes:
            genes.append(gene)
    return genes


def _extract_gene_token(text: str) -> str | None:
    cleaned = text.strip(" ,;:.")
    cleaned = re.sub(r"^(?:the|both)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        return None

    tokens = cleaned.split()
    while tokens and tokens[-1].lower() in TRAILING_CONTEXT_TOKENS:
        tokens.pop()
    if not tokens:
        return None

    for token in reversed(tokens):
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9/-]*", token):
            return token

    return None


def _strip_context_prefix(text: str) -> str:
    prefixes = [
        r"^In\s+[^,]+,\s*",
        r"^Within\s+[^,]+,\s*",
        r"^In\s+[^,]+\scells,\s*",
    ]
    cleaned = text
    for pattern in prefixes:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return cleaned


def _is_valid_sentence(sentence: str) -> bool:
    return any(pattern.fullmatch(sentence) for pattern in CANONICAL_RELATION_PATTERNS)


def _log_rejection(original_input: str, raw_output: str, sanitized_output: str, reason: str) -> None:
    if os.getenv("OPTIMIZER_LOG_REJECTIONS", "").strip().lower() != "true":
        return

    logger.warning(
        "Rejected or partially accepted optimizer output. reason=%s\ninput=%s\nraw_output=%s\nsanitized_output=%s",
        reason,
        original_input,
        raw_output,
        sanitized_output,
    )
