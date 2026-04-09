import logging

import httpx

from backend.nlp.local_text_optimizer import optimize_text


class MockResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "request failed",
                request=httpx.Request("POST", "http://localhost"),
                response=httpx.Response(self.status_code),
            )

    def json(self):
        return self._payload


def _set_ollama_env(monkeypatch):
    monkeypatch.setenv("LOCAL_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")


def test_optimize_text_expands_source_conjunction(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "GATA4 and GATA6 directly activate HAND2 expression."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("GATA4 and GATA6 directly activate HAND2 expression.")

    assert result.text == "GATA4 activates HAND2. GATA6 activates HAND2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_expands_multiple_targets(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "IRX4 activates both HAND1 and HAND2."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("IRX4 activates both HAND1 and HAND2.")

    assert result.text == "IRX4 activates HAND1. IRX4 activates HAND2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_recovers_passive_expression_activation(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "HEY2 is upregulated."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("Expression of HEY2 is increased by NOTCH signalling.")

    assert result.text == "NOTCH activates HEY2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_recovers_passive_expression_inhibition(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "HEY2 is downregulated."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("HEY2 expression is repressed by TBX5.")

    assert result.text == "TBX5 inhibits HEY2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_recovers_loss_of_expression_knockout(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "NPPA expression is decreased."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("Loss of TBX5 leads to decreased expression of NPPA.")

    assert result.text == "TBX5 knockout inhibits NPPA."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_supports_knockout_normalization(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "IRX4 expression is lost by HAND2 knockout."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("IRX4 expression is lost by HAND2 knockout.")

    assert result.text == "HAND2 knockout inhibits IRX4."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_preserves_more_relations_for_full_example(monkeypatch):
    _set_ollama_env(monkeypatch)

    original_text = (
        "GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. "
        "IRX4 expression is lost by HAND2 knockout.IRX4 contributes to activating MYL2. "
        "IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. "
        "NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. "
        "Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. "
        "Expression of HEY2 is increased by NOTCH signalling. NOTCH activates NOTCH."
    )
    optimized_output = (
        "GATA46 activates HAND2. GATA46 activates HEY2. IRX4 activates HAND2. "
        "NR2F2 inhibits IRX4. NR2F2 inhibits MYL2. NR2F2 inhibits HEY2. NOTCH activates NOTCH."
    )

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": optimized_output}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text(original_text)

    assert "GATA46 activates HEY2." in result.text
    assert "GATA46 activates HAND2." in result.text
    assert "IRX4 activates HAND2." in result.text
    assert "NR2F2 inhibits IRX4." in result.text
    assert "NR2F2 inhibits MYL2." in result.text
    assert "NR2F2 inhibits HEY2." in result.text
    assert "NOTCH activates HEY2." in result.text
    assert "NOTCH activates NOTCH." in result.text
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_rejects_malformed_knockout_target(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "NR2F2 binds knockout."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    original_text = "NR2F2 binds knockout."
    result = optimize_text(original_text)

    assert result.text == original_text
    assert result.optimized is False
    assert result.fallback is True


def test_optimize_text_rejects_unsupported_broad_targets(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "IRX activates atrial genes."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    original_text = "IRX activates atrial genes."
    result = optimize_text(original_text)

    assert result.text == original_text
    assert result.optimized is False
    assert result.fallback is True


def test_optimize_text_merges_original_and_optimized_without_duplicates(monkeypatch):
    _set_ollama_env(monkeypatch)

    original_text = "Expression of HEY2 is increased by NOTCH signalling. NOTCH activates NOTCH."

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "NOTCH activates NOTCH."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text(original_text)

    assert result.text == "NOTCH activates HEY2. NOTCH activates NOTCH."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_normalizes_self_relations(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "NOTCH activates itself. SCR binds its own promoter."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("NOTCH activates NOTCH. SCR binds SCR.")

    assert "NOTCH activates NOTCH." in result.text
    assert "SCR binds SCR." in result.text
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_logs_rejection_when_enabled(monkeypatch, caplog):
    _set_ollama_env(monkeypatch)
    monkeypatch.setenv("OPTIMIZER_LOG_REJECTIONS", "true")

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "This is a summary of the relationships."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    with caplog.at_level(logging.WARNING):
        result = optimize_text("GATA4 activates HAND2 expression.")

    assert result.text == "GATA4 activates HAND2 expression."
    assert result.optimized is False
    assert result.fallback is True
    assert "no valid relation sentences remained after normalization" in caplog.text


def test_optimize_text_does_not_log_rejection_when_disabled(monkeypatch, caplog):
    _set_ollama_env(monkeypatch)
    monkeypatch.delenv("OPTIMIZER_LOG_REJECTIONS", raising=False)

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": "This is a summary of the relationships."}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    with caplog.at_level(logging.WARNING):
        result = optimize_text("GATA4 activates HAND2 expression.")

    assert result.text == "GATA4 activates HAND2 expression."
    assert result.optimized is False
    assert result.fallback is True
    assert caplog.text == ""


def test_optimize_text_falls_back_when_ollama_unavailable(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    original_text = "GATA4 activates HAND2 expression."
    result = optimize_text(original_text)

    assert result.text == original_text
    assert result.optimized is False
    assert result.fallback is True


def test_optimize_text_falls_back_without_model(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.setenv("LOCAL_LLM_PROVIDER", "ollama")

    original_text = "GATA4 activates HAND2 expression."
    result = optimize_text(original_text)

    assert result.text == original_text
    assert result.optimized is False
    assert result.fallback is True
