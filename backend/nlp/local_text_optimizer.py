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
    "stimulates",
    "stimulate",
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
PASSIVE_ACTIVATION_WORDS = ("increased", "enhanced", "activated", "induced", "promoted", "upregulated")
PASSIVE_INHIBITION_WORDS = ("repressed", "reduced", "decreased", "suppressed", "downregulated", "lost", "absent")
TRAILING_CONTEXT_TOKENS = {
    "cm", "cms", "cell", "cells", "ventricle", "ventricles", "ventricular", "atrial",
    "cardiac", "derived", "human", "induced", "pluripotent", "stem", "mice", "mouse",
    "in", "of", "the", "a", "an", "development", "heart", "hearts", "progenitors",
    "transcription", "activity",
}
GENERIC_INVALID_TOKENS = {
    "knockout", "mutant", "signalling", "signaling", "expression", "promoter", "loci",
    "genes", "gene", "transcription", "cells", "cell", "ventricles", "ventricle",
    "proteins", "protein", "elements", "regions", "sites",
}

SYSTEM_PROMPT = """You convert biological prose into short parser-friendly relation statements.
Rules:
- Keep only explicit gene-gene or gene-expression relations supported by the app.
- Split multi-relation sentences into separate sentences.
- Output one relation per sentence when possible.
- Use only these relation verbs when possible: activates, inhibits, binds.
- Use "X knockout inhibits Y" when the text says Y expression is lost/reduced in X knockout or X mutant conditions.
- Preserve explicit regulation statements including expression increased/repressed by X.
- Do not explain.
- Do not summarize.
- Do not include bullets.
- Output plain sentences only.
- Do not replace explicit genes with pronouns or generic terms.
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

    sanitized_output = _sanitize_text(raw_output)
    original_relations, original_dropped = _extract_valid_relations(cleaned_input)
    optimized_relations, optimized_dropped = _extract_valid_relations(sanitized_output)

    merged = _merge_relations(original_relations, optimized_relations)
    dropped_reasons = [*original_dropped, *optimized_dropped]

    if not merged:
        _log_rejection(
            cleaned_input,
            raw_output,
            sanitized_output,
            "no valid relation sentences remained after normalization",
        )
        return OptimizationResult(text=text, optimized=False, fallback=True)

    if dropped_reasons:
        _log_rejection(cleaned_input, raw_output, sanitized_output, "; ".join(dropped_reasons))

    return OptimizationResult(text=" ".join(merged), optimized=True, fallback=False)


def _request_ollama(base_url: str, model: str, text: str, timeout: float) -> str:
    response = httpx.post(
        f"{base_url}/api/chat",
        json={
            "model": model,
            "stream": False,
            "options": {"temperature": 0, "top_p": 1},
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


def _sanitize_text(text: str) -> str:
    sanitized = text.strip()
    sanitized = re.sub(r"```(?:text)?", "", sanitized, flags=re.IGNORECASE)
    sanitized = sanitized.replace("```", "")
    sanitized = re.sub(r"(^|\s)([-*•]|\d+\.)\s+", r"\1", sanitized)
    sanitized = re.sub(r"([a-z)])\.([A-Z])", r"\1. \2", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    sanitized = re.sub(r"\s+\.", ".", sanitized)
    return sanitized


def _extract_valid_relations(text: str) -> tuple[list[str], list[str]]:
    kept: list[str] = []
    dropped: list[str] = []

    for sentence in _split_candidate_sentences(text):
        relations, reason = _extract_relations_from_sentence(sentence)
        if relations:
            for relation in relations:
                if _is_valid_sentence(relation) and relation not in kept:
                    kept.append(relation)
        elif reason:
            dropped.append(f"dropped sentence: {reason}: {sentence.strip()}")

    return kept, dropped


def _split_candidate_sentences(text: str) -> list[str]:
    sanitized = _sanitize_text(text)
    if not sanitized:
        return []
    return [sentence.strip() for sentence in re.split(r"(?<=\.)\s+", sanitized) if sentence.strip()]


def _extract_relations_from_sentence(sentence: str) -> tuple[list[str], str | None]:
    cleaned = sentence.strip()
    if not cleaned:
        return [], None

    lowered = cleaned.lower()
    if any(marker in lowered for marker in EXPLANATION_MARKERS):
        return [], "explanatory text"

    cleaned = cleaned.rstrip(".").strip()
    cleaned = _strip_context_prefix(cleaned)
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    cleaned = re.sub(r",", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;:")

    clauses = _split_relation_clauses(cleaned)
    relations: list[str] = []
    reasons: list[str] = []
    for clause in clauses:
        clause_relations, reason = _extract_clause_relations(clause)
        if clause_relations:
            for relation in clause_relations:
                if relation not in relations:
                    relations.append(relation)
        elif reason:
            reasons.append(reason)

    if relations:
        return relations, None
    if reasons:
        return [], reasons[0]
    return [], "no supported relation found"


def _split_relation_clauses(cleaned: str) -> list[str]:
    clauses = [cleaned]
    splitters = [
        r"\s+and expression is\s+",
        r"\s+and HEY2 expression is\s+",
        r"\s+and MYL7 expression is\s+",
    ]
    for splitter in splitters:
        next_clauses: list[str] = []
        for clause in clauses:
            next_clauses.extend([part.strip() for part in re.split(splitter, clause, flags=re.IGNORECASE) if part.strip()])
        clauses = next_clauses
    return clauses


def _extract_clause_relations(clause: str) -> tuple[list[str], str | None]:
    passive_knockout = _extract_knockout_relations(clause)
    if passive_knockout:
        return passive_knockout, None

    loss_knockout = _extract_loss_of_relations(clause)
    if loss_knockout:
        return loss_knockout, None

    passive_expression = _extract_passive_expression_relations(clause)
    if passive_expression:
        return passive_expression, None

    active_relations = _extract_active_voice_relations(clause)
    if active_relations:
        return active_relations, None

    return [], "no supported relation verb after normalization"


def _extract_knockout_relations(clause: str) -> list[str]:
    patterns = [
        r"^([A-Za-z][A-Za-z0-9/-]*)\s+(?:expression\s+)?is\s+(?:lost|absent|reduced|decreased)\s+by\s+([A-Za-z][A-Za-z0-9/-]*)(?:\s+(?:knockout|mutant))(?:\b.*)?$",
        r"^([A-Za-z][A-Za-z0-9/-]*)\s+(?:expression\s+)?is\s+(?:lost|absent|reduced|decreased)\s+in\s+([A-Za-z][A-Za-z0-9/-]*)(?:\s+(?:knockout|mutant))(?:\b.*)?$",
        r"^expression of\s+([A-Za-z][A-Za-z0-9/-]*)\s+is\s+(?:lost|absent|reduced|decreased)\s+by\s+([A-Za-z][A-Za-z0-9/-]*)(?:\s+(?:knockout|mutant))(?:\b.*)?$",
        r"^expression of\s+([A-Za-z][A-Za-z0-9/-]*)\s+is\s+(?:lost|absent|reduced|decreased)\s+in\s+([A-Za-z][A-Za-z0-9/-]*)(?:\s+(?:knockout|mutant))(?:\b.*)?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, clause, flags=re.IGNORECASE)
        if match:
            target, source = match.groups()
            target_gene = _canonical_gene(target)
            source_gene = _canonical_gene(source)
            if target_gene and source_gene:
                return [f"{source_gene} knockout inhibits {target_gene}."]
    knockout_relation_match = re.match(
        r"^([A-Za-z][A-Za-z0-9/-]*)\s+knockout\s+(inhibits|leads to)\s+([A-Za-z][A-Za-z0-9/-]*)$",
        clause,
        flags=re.IGNORECASE,
    )
    if knockout_relation_match:
        source, relation, target = knockout_relation_match.groups()
        source_gene = _canonical_gene(source)
        target_gene = _canonical_gene(target)
        if source_gene and target_gene:
            return [f"{source_gene} knockout {relation.lower()} {target_gene}."]
    return []


def _extract_loss_of_relations(clause: str) -> list[str]:
    match = re.match(
        r"^loss of\s+([A-Za-z][A-Za-z0-9/-]*)\s+leads to\s+(?:decreased|reduced|lost|absent)\s+(?:expression of\s+)?([A-Za-z][A-Za-z0-9/-]*)$",
        clause,
        flags=re.IGNORECASE,
    )
    if not match:
        return []
    source, target = match.groups()
    source_gene = _canonical_gene(source)
    target_gene = _canonical_gene(target)
    if source_gene and target_gene:
        return [f"{source_gene} knockout inhibits {target_gene}."]
    return []


def _extract_passive_expression_relations(clause: str) -> list[str]:
    passive_patterns = [
        r"^expression of\s+(.+?)\s+is\s+([A-Za-z-]+)\s+by\s+(.+)$",
        r"^(.+?)\s+expression\s+is\s+([A-Za-z-]+)\s+by\s+(.+)$",
    ]
    for pattern in passive_patterns:
        match = re.match(pattern, clause, flags=re.IGNORECASE)
        if not match:
            continue
        target_text, relation_word, source_text = match.groups()
        relation = _relation_from_passive_word(relation_word)
        if relation is None:
            return []
        sources = _expand_gene_list(_strip_signal_suffix(source_text))
        targets = _expand_gene_list(target_text)
        if not sources:
            return []
        if not targets:
            return []
        return [f"{source} {relation} {target}." for source in sources for target in targets]
    return []


def _extract_active_voice_relations(clause: str) -> list[str]:
    normalized = clause
    normalized = re.sub(r"\bbinds to genomic loci of\b", "binds", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bbinds promoter of\b", "binds", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bbinds to regulatory regions of\b", "binds", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bbinds to\b", "binds", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bexpression of\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bgene expression\b", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bexpression\b", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bgene\b", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bdirectly\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\balso\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bboth\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip(" ,;:")

    for verb in ACTIVATION_VERBS:
        normalized = re.sub(rf"\b{re.escape(verb)}\b", "activates", normalized, flags=re.IGNORECASE)
    for verb in INHIBITION_VERBS:
        normalized = re.sub(rf"\b{re.escape(verb)}\b", "inhibits", normalized, flags=re.IGNORECASE)

    match = re.match(
        r"^(.+?)\s+(activates|inhibits|binds|leads to)\s+(.+)$",
        normalized,
        flags=re.IGNORECASE,
    )
    if not match:
        return []

    source_text, relation, target_text = match.groups()
    sources = _expand_gene_list(_strip_signal_suffix(source_text))
    if not sources:
        return []

    self_targets = _normalize_self_relation_targets(target_text, relation, sources)
    if self_targets:
        return self_targets

    cleaned_target_text = re.split(r"\s+and\s+expression\s+is\s+", target_text, maxsplit=1, flags=re.IGNORECASE)[0]
    targets = _expand_gene_list(cleaned_target_text)
    if not targets:
        return []
    if any(target.lower() in GENERIC_INVALID_TOKENS for target in targets):
        return []

    return [f"{source} {relation.lower()} {target}." for source in sources for target in targets]


def _normalize_self_relation_targets(target_text: str, relation: str, sources: list[str]) -> list[str]:
    lowered_target = target_text.strip().lower().rstrip(".")
    self_patterns = ("itself", "its own expression", "its own promoter")
    if lowered_target not in self_patterns:
        return []
    return [f"{source} {relation.lower()} {source}." for source in sources]


def _relation_from_passive_word(word: str) -> str | None:
    lowered = word.lower()
    if lowered in PASSIVE_ACTIVATION_WORDS:
        return "activates"
    if lowered in PASSIVE_INHIBITION_WORDS:
        return "inhibits"
    return None


def _strip_signal_suffix(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"\b(signalling|signaling)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;:")
    return cleaned


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
        gene = _canonical_gene(token)
        if gene:
            return gene
    return None


def _canonical_gene(token: str) -> str | None:
    cleaned = token.strip(" ,;:.")
    cleaned = re.sub(r"\b(signalling|signaling)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return None
    if cleaned.lower() in GENERIC_INVALID_TOKENS:
        return None
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9/-]*", cleaned):
        return cleaned
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


def _merge_relations(*relation_groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in relation_groups:
        for relation in group:
            if relation not in merged:
                merged.append(relation)
    return merged


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
