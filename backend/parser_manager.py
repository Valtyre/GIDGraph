# file: backend/parser_manager.py

from backend.nlp.local_text_optimizer import normalize_parser_text
from backend.nlp.natural_language_processor import nlp_runner
from backend.parser.visParser import ParserError, vis_parse_text


def _normalize_or_raise(source_text: str, parser_candidate: str) -> str:
    normalized = normalize_parser_text(parser_candidate)
    if not normalized.relations:
        raise ParserError(
            error="NO_VALID_RELATIONS",
            message="No supported gene relations could be extracted from the provided text.",
            original_input=source_text,
            parser_input=normalized.text,
        )
    return normalized.text


def process_nl_text(nl_text: str) -> tuple[str, dict]:
    """
    Master function to take any natural language text,
    run the NLP pipeline, parse it, and return (SNL, graph_dict).
    """
    nlp_output = nlp_runner(nl_text)
    normalized_text = _normalize_or_raise(nl_text, nlp_output)

    transformer = vis_parse_text(normalized_text, original_input=nl_text)
    graph_dict = transformer.get_vis_data()

    return normalized_text, graph_dict


def process_snl_only(snl_text: str) -> dict[str, list]:
    """
    Takes already-edited SNL text, normalizes it, parses it,
    and returns the graph dict.
    """
    normalized_text = _normalize_or_raise(snl_text, snl_text)
    transformer = vis_parse_text(normalized_text, original_input=snl_text)
    return transformer.get_vis_data()
