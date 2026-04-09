"""
Tests for parser-bound normalization and pipeline behavior.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest

from backend.nlp.local_text_optimizer import normalize_parser_text
from backend.parser.visParser import ParserError
from backend.parser_manager import process_nl_text


def test_normalize_parser_text_keeps_valid_relations_and_drops_generic_targets():
    result = normalize_parser_text(
        "GATA4 activates HAND2. and binds promoter. SCR binds its own promoter. CLE40p inhibits roots."
    )

    assert result.text == "GATA4 activates HAND2. SCR binds SCR."
    assert "GATA4 activates HAND2." in result.relations
    assert "SCR binds SCR." in result.relations
    assert any("promoter" in dropped for dropped in result.dropped)
    assert any("roots" in dropped for dropped in result.dropped)


def test_process_nl_text_preserves_partial_graph_when_some_relations_are_valid(monkeypatch):
    monkeypatch.setattr(
        "backend.parser_manager.nlp_runner",
        lambda text: "GATA4 activates HAND2. and binds promoter. SCR binds its own promoter.",
    )

    normalized_text, graph = process_nl_text("source text")

    assert normalized_text == "GATA4 activates HAND2. SCR binds SCR."
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2


def test_process_nl_text_raises_when_no_valid_relations_remain(monkeypatch):
    monkeypatch.setattr(
        "backend.parser_manager.nlp_runner",
        lambda text: "and binds promoter. genes inhibits auxin.",
    )

    with pytest.raises(ParserError) as exc_info:
        process_nl_text("source text")

    assert exc_info.value.error == "NO_VALID_RELATIONS"
