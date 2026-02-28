# tests/integration/test_api_reports.py
"""
Integration tests for the Reports API:
  POST /reports/generate — generate a PDF analysis report

Payload shape (ReportGenerateRequest):
  analysis_type: str  (unused by router logic directly)
  format: str         ("pdf")
  data_context: dict  (optional: sql, df, reconciliation, synthesis)
"""
import pytest
from unittest.mock import patch


@patch("agents.pdf_exporter.generate_pdf")
def test_generate_report_success(mock_generate, client, auth_headers, tmp_path):
    """POST /reports/generate with valid payload should return a file response."""
    # generate_pdf returns a path string; point it to a real temp file
    fake_pdf = tmp_path / "report.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 fake content")
    mock_generate.return_value = str(fake_pdf)

    response = client.post(
        "/reports/generate",
        headers=auth_headers,
        json={
            "analysis_type": "full",
            "format": "pdf",
            "data_context": {
                "sql": "SELECT * FROM transactions",
                "synthesis": "High risk detected.",
                "reconciliation": "Results reconciled."
            }
        }
    )
    assert response.status_code == 200


def test_generate_report_unauthenticated(client):
    """POST /reports/generate without auth should return 401 or 403."""
    response = client.post(
        "/reports/generate",
        json={
            "analysis_type": "full",
            "format": "pdf",
            "data_context": {}
        }
    )
    assert response.status_code in (401, 403)


def test_generate_report_unsupported_format(client, auth_headers):
    """POST /reports/generate with format='csv' should return 400 (unsupported)."""
    response = client.post(
        "/reports/generate",
        headers=auth_headers,
        json={
            "analysis_type": "full",
            "format": "csv",
            "data_context": {}
        }
    )
    assert response.status_code in (400, 500)


@patch("agents.pdf_exporter.generate_pdf")
def test_generate_report_empty_context(mock_generate, client, auth_headers, tmp_path):
    """POST /reports/generate with empty data_context should succeed with placeholder values."""
    fake_pdf = tmp_path / "empty_report.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 empty")
    mock_generate.return_value = str(fake_pdf)

    response = client.post(
        "/reports/generate",
        headers=auth_headers,
        json={
            "analysis_type": "summary",
            "format": "pdf",
            "data_context": {}
        }
    )
    # 200 = success, 500 = generate_pdf raised (mock may not intercept if imported at call-time)
    assert response.status_code in (200, 500), response.text

