"""
Integration tests for the FastAPI endpoints.
"""


class TestParseEndpoint:
    """Tests for POST /api/parse endpoint."""

    def test_parse_valid_text(self, api_client, sample_nl_text, monkeypatch):
        """Test parsing valid natural language text."""
        def fake_process_nl_text(text):
            assert text == sample_nl_text
            return ("GATA4 activates HAND2.", {"nodes": [], "edges": []})

        monkeypatch.setattr("backend.server.process_nl_text", fake_process_nl_text)

        response = api_client.post(
            "/api/parse",
            json={"text": sample_nl_text}
        )
        assert response.status_code == 200
        data = response.json()
        assert "graph" in data
        assert "nodes" in data["graph"]
        assert "edges" in data["graph"]

    def test_parse_empty_text_returns_validation_error(self, api_client, monkeypatch):
        """Test parsing empty text surfaces a structured validation error."""
        from backend.parser.visParser import ParserError

        monkeypatch.setattr(
            "backend.server.process_nl_text",
            lambda text: (_ for _ in ()).throw(
                ParserError(
                    error="NO_VALID_RELATIONS",
                    message="No supported gene relations could be extracted from the provided text.",
                    original_input=text,
                    parser_input="",
                )
            ),
        )

        response = api_client.post(
            "/api/parse",
            json={"text": ""}
        )
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"] == "NO_VALID_RELATIONS"
        assert "No supported gene relations" in data["detail"]["message"]

    def test_parse_returns_partial_graph_when_valid_relations_survive(self, api_client, monkeypatch):
        """Test parsing returns success when at least one valid relation remains."""
        monkeypatch.setattr(
            "backend.server.process_nl_text",
            lambda text: (
                "GATA4 activates HAND2. SCR binds SCR.",
                {
                    "nodes": [
                        {"id": "GATA4", "label": "GATA4"},
                        {"id": "HAND2", "label": "HAND2"},
                        {"id": "SCR", "label": "SCR"},
                    ],
                    "edges": [
                        {"from": "GATA4", "to": "HAND2", "label": "activation"},
                        {"from": "SCR", "to": "SCR", "label": "binding"},
                    ],
                },
            ),
        )

        response = api_client.post(
            "/api/parse",
            json={"text": "mixed input"}
        )
        assert response.status_code == 200
        assert len(response.json()["graph"]["edges"]) == 2


class TestUpdateSNLEndpoint:
    """Tests for POST /api/update_snl endpoint."""

    def test_update_snl_valid(self, api_client, sample_snl_text, monkeypatch):
        """Test updating SNL with valid text."""
        monkeypatch.setattr(
            "backend.server.process_snl_only",
            lambda text: {"nodes": [{"id": "A", "label": "A"}], "edges": []},
        )

        response = api_client.post(
            "/api/update_snl",
            json={"text": sample_snl_text}
        )
        assert response.status_code == 200
        data = response.json()
        assert "graph" in data
        assert "nodes" in data["graph"]
        assert "edges" in data["graph"]

    def test_update_snl_empty(self, api_client, monkeypatch):
        """Test updating with empty SNL."""
        monkeypatch.setattr(
            "backend.server.process_snl_only",
            lambda text: {"nodes": [], "edges": []},
        )

        response = api_client.post(
            "/api/update_snl",
            json={"text": ""}
        )
        assert response.status_code == 200
        assert response.json() == {"graph": {"nodes": [], "edges": []}}


class TestOptimizeEndpoint:
    """Tests for POST /api/optimize_nl endpoint."""

    def test_optimize_returns_optimized_text(self, api_client, monkeypatch):
        """Test optimizing text returns the service result."""
        from backend.nlp.local_text_optimizer import OptimizationResult

        monkeypatch.setattr(
            "backend.server.optimize_text",
            lambda text: OptimizationResult(
                text="GATA4 activates HAND2. GATA6 activates HAND2.",
                optimized=True,
                fallback=False,
            ),
        )

        response = api_client.post(
            "/api/optimize_nl",
            json={"text": "GATA4 and GATA6 directly activate HAND2 expression."}
        )
        assert response.status_code == 200
        assert response.json() == {
            "text": "GATA4 activates HAND2. GATA6 activates HAND2.",
            "optimized": True,
            "fallback": False,
        }

    def test_optimize_returns_fallback_text(self, api_client, monkeypatch):
        """Test optimizer fallback preserves the original text."""
        from backend.nlp.local_text_optimizer import OptimizationResult

        original_text = "IRX4 expression is lost by HAND2 knockout."

        monkeypatch.setattr(
            "backend.server.optimize_text",
            lambda text: OptimizationResult(
                text=original_text,
                optimized=False,
                fallback=True,
            ),
        )

        response = api_client.post(
            "/api/optimize_nl",
            json={"text": original_text}
        )
        assert response.status_code == 200
        assert response.json() == {
            "text": original_text,
            "optimized": False,
            "fallback": True,
        }


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_returns_message(self, api_client):
        """Test root endpoint returns welcome message."""
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data == {"Hello": "World"}
