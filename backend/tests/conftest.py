"""
Pytest configuration and fixtures for backend tests.
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_client():
    """Create a test client for the FastAPI app."""
    from backend.server import app
    return TestClient(app)


@pytest.fixture
def sample_nl_text():
    """Sample natural language text for NLP testing."""
    return "GATA4 activates HAND2 expression. NR2F2 represses IRX4 gene expression."


@pytest.fixture
def sample_snl_text():
    """Sample SNL text for parser testing."""
    return "GATA4 activates HAND2. NR2F2 inhibits IRX4."


@pytest.fixture
def sample_graph():
    """Sample graph structure for export testing."""
    return {
        "nodes": [
            {"id": "GATA4", "label": "GATA4"},
            {"id": "HAND2", "label": "HAND2"},
        ],
        "edges": [
            {"from": "GATA4", "to": "HAND2", "label": "activation"}
        ]
    }


@pytest.fixture
def sample_logical_formulas():
    """Sample logical formulas for export testing."""
    return [
        {
            "gene": "HAND2",
            "formula": "GATA4",
            "activators": ["GATA4"],
            "inhibitors": []
        }
    ]
