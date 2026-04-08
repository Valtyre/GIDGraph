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
        return MockResponse(
            {"message": {"content": "GATA4 and GATA6 directly activate HAND2 expression."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("GATA4 and GATA6 directly activate HAND2 expression.")

    assert result.text == "GATA4 activates HAND2. GATA6 activates HAND2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_expands_multiple_targets(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "IRX4 activates both HAND1 and HAND2."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("IRX4 activates both HAND1 and HAND2.")

    assert result.text == "IRX4 activates HAND1. IRX4 activates HAND2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_expands_inhibition_targets(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "NR2F2 inhibits IRX4 and MYL2."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("NR2F2 inhibits IRX4 and MYL2.")

    assert result.text == "NR2F2 inhibits IRX4. NR2F2 inhibits MYL2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_supports_knockout_normalization(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "IRX4 expression is lost by HAND2 knockout."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("IRX4 expression is lost by HAND2 knockout.")

    assert result.text == "HAND2 knockout inhibits IRX4."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_strips_parenthetical_qualifiers(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {
                "message": {
                    "content": "In mice cells, GATA proteins (together with TBX20) enhance HEY2 expression in ventricular CMs."
                }
            }
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("Text")

    assert result.text == "GATA activates HEY2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_tolerates_knockout_parenthetical_qualifiers(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {
                "message": {
                    "content": "In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs."
                }
            }
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("Text")

    assert result.text == "HAND2 knockout inhibits IRX4."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_preserves_more_relations_for_long_example(monkeypatch):
    _set_ollama_env(monkeypatch)

    long_output = (
        "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. "
        "In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. "
        "In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. "
        "IRX contributes to activating ventricular genes and supressing atrial genes. "
        "IRX4 activates both HAND1 and HAND2. "
        "IRX4 activates also HAND1."
    )

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": long_output}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("Text")

    assert result.text == (
        "GATA6 activates HAND2. "
        "GATA4 activates HAND2. "
        "GATA activates HEY2. "
        "HAND2 knockout inhibits IRX4. "
        "IRX4 activates HAND1. "
        "IRX4 activates HAND2."
    )
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_omits_ambiguous_broad_statement(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {
                "message": {
                    "content": "IRX contributes to activating ventricular genes and suppressing atrial genes."
                }
            }
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    original_text = "IRX contributes to activating ventricular genes and suppressing atrial genes."
    result = optimize_text(original_text)

    assert result.text == original_text
    assert result.optimized is False
    assert result.fallback is True


def test_optimize_text_normalizes_binding_phrase(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "NR2F2 binds to genomic loci of MYL7."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("NR2F2 binds to genomic loci of MYL7.")

    assert result.text == "NR2F2 binds MYL7."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_repairs_missing_sentence_boundary(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "HAND2 knockout inhibits IRX4.IRX4 activates HAND2."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("IRX4 expression is lost by HAND2 knockout. IRX4 activates HAND2.")

    assert result.text == "HAND2 knockout inhibits IRX4. IRX4 activates HAND2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_deduplicates_duplicate_relations(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("Text")

    assert result.text == "IRX4 activates HAND1. IRX4 activates HAND2."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_normalizes_self_activation(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "NOTCH activates itself."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("NOTCH activates NOTCH.")

    assert result.text == "NOTCH activates NOTCH."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_normalizes_self_inhibition(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "NOTCH inhibits itself."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("NOTCH inhibits NOTCH.")

    assert result.text == "NOTCH inhibits NOTCH."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_normalizes_self_binding(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "NOTCH binds itself."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("NOTCH binds NOTCH.")

    assert result.text == "NOTCH binds NOTCH."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_normalizes_own_expression_to_self_activation(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "NOTCH activates its own expression."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("NOTCH activates NOTCH.")

    assert result.text == "NOTCH activates NOTCH."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_normalizes_own_promoter_to_self_binding(monkeypatch):
    _set_ollama_env(monkeypatch)

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "SCR binds its own promoter."}}
        )

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("SCR binds SCR.")

    assert result.text == "SCR binds SCR."
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_preserves_explicit_notch_self_loop_in_long_example(monkeypatch):
    _set_ollama_env(monkeypatch)

    long_output = (
        "GATA46 enhances HEY2 expression. "
        "GATA46 directly activates HAND2 expression. "
        "IRX4 expression is lost by HAND2 knockout. "
        "IRX4 contributes to activating MYL2. "
        "IRX4 activates HAND2. "
        "NR2F2 represses IRX4 gene expression. "
        "NR2F2 represses MYL2. "
        "NR2F2 represses HEY2 gene. "
        "NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. "
        "Ectopic MYL7 expression is observed in HEY2 knockout ventricles. "
        "Expression of HEY2 is increased by NOTCH signalling. "
        "NOTCH activates itself."
    )

    def fake_post(url, json, timeout):
        return MockResponse({"message": {"content": long_output}})

    monkeypatch.setattr("backend.nlp.local_text_optimizer.httpx.post", fake_post)

    result = optimize_text("Text")

    assert "NOTCH activates NOTCH." in result.text
    assert result.optimized is True
    assert result.fallback is False


def test_optimize_text_logs_rejection_when_enabled(monkeypatch, caplog):
    _set_ollama_env(monkeypatch)
    monkeypatch.setenv("OPTIMIZER_LOG_REJECTIONS", "true")

    def fake_post(url, json, timeout):
        return MockResponse(
            {"message": {"content": "This is a summary of the relationships."}}
        )

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
        return MockResponse(
            {"message": {"content": "This is a summary of the relationships."}}
        )

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
