import json

from myth_forge_api.print_acceptance import run_print_quote_acceptance


def test_print_quote_acceptance_creates_safe_local_quote() -> None:
    result = run_print_quote_acceptance()

    report_text = json.dumps(result.report)
    assert result.exit_code == 0
    assert result.report["kind"] == "print_quote_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["candidate_format"] == "3mf"
    assert result.report["candidate_uri"].endswith(".3mf")
    assert result.report["quote_status"] == "draft_quote"
    assert result.report["provider"] == "local_stub"
    assert result.report["currency"] == "USD"
    assert result.report["estimated_price_cents"] == 1600
    assert result.report["requires_user_approval"] is True
    assert result.report["safety"]["provider_secrets_in_report"] is False
    assert result.report["safety"]["checkout_identifiers_in_report"] is False
    assert "api_key" not in report_text.lower()
    assert "checkout_url" not in report_text
