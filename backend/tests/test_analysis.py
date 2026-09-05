import io


def _upload_ready_paper(client, headers, minimal_pdf_bytes):
    resp = client.post(
        "/api/papers", headers=headers, files={"file": ("p.pdf", io.BytesIO(minimal_pdf_bytes), "application/pdf")}
    )
    return resp.json()["id"]


def test_summarize_requires_ownership(client, auth_headers, minimal_pdf_bytes):
    headers, _ = auth_headers
    paper_id = _upload_ready_paper(client, headers, minimal_pdf_bytes)

    other = client.post("/api/auth/register", json={"email": "analysis-other@example.com", "password": "SecurePass123"})
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    resp = client.post(f"/api/papers/{paper_id}/summarize", headers=other_headers)
    assert resp.status_code == 404


def test_summarize_generates_summary_from_sections(client, auth_headers, minimal_pdf_bytes):
    headers, _ = auth_headers
    paper_id = _upload_ready_paper(client, headers, minimal_pdf_bytes)

    resp = client.post(f"/api/papers/{paper_id}/summarize", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["summary"]


def test_compare_requires_at_least_two_papers(client, auth_headers, minimal_pdf_bytes):
    headers, _ = auth_headers
    paper_id = _upload_ready_paper(client, headers, minimal_pdf_bytes)

    resp = client.post("/api/papers/compare", headers=headers, json={"paper_ids": [paper_id]})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INSUFFICIENT_PAPERS"


def test_compare_two_papers_returns_structured_result(client, auth_headers, minimal_pdf_bytes):
    headers, _ = auth_headers
    paper_a = _upload_ready_paper(client, headers, minimal_pdf_bytes)
    paper_b = _upload_ready_paper(client, headers, minimal_pdf_bytes)

    resp = client.post("/api/papers/compare", headers=headers, json={"paper_ids": [paper_a, paper_b]})
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["comparison"].keys()) == {
        "research_problem", "methodology", "datasets", "models",
        "results", "strengths", "limitations", "key_differences",
    }
