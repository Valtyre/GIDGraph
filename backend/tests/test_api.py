"""
Integration tests for the FastAPI endpoints.
"""
import pytest


class TestParseEndpoint:
    """Tests for POST /api/parse endpoint."""

    def test_parse_valid_text(self, api_client, sample_nl_text):
        """Test parsing valid natural language text."""
        response = api_client.post(
            "/api/parse",
            json={"text": sample_nl_text}
        )
        assert response.status_code == 200
        data = response.json()
        assert "snl" in data
        assert "graph" in data
        assert "nodes" in data["graph"]
        assert "edges" in data["graph"]

    def test_parse_empty_text(self, api_client):
        """Test parsing empty text returns empty result."""
        response = api_client.post(
            "/api/parse",
            json={"text": ""}
        )
        assert response.status_code == 200
        data = response.json()
        assert "snl" in data
        assert "graph" in data


class TestUpdateSNLEndpoint:
    """Tests for POST /api/update_snl endpoint."""

    def test_update_snl_valid(self, api_client, sample_snl_text):
        """Test updating SNL with valid text."""
        response = api_client.post(
            "/api/update_snl",
            json={"snl": sample_snl_text}
        )
        assert response.status_code == 200
        data = response.json()
        assert "graph" in data
        assert "nodes" in data["graph"]
        assert "edges" in data["graph"]

    def test_update_snl_empty(self, api_client):
        """Test updating with empty SNL."""
        response = api_client.post(
            "/api/update_snl",
            json={"snl": ""}
        )
        assert response.status_code == 200


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_returns_message(self, api_client):
        """Test root endpoint returns welcome message."""
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
