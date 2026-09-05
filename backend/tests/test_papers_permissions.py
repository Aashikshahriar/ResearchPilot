import io


def _register(client, email):
    resp = client.post("/api/auth/register", json={"email": email, "password": "SecurePass123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_requires_pdf_content_type(client, auth_headers):
    headers, _ = auth_headers
    resp = client.post(
        "/api/papers",
        headers=headers,
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"


def test_user_cannot_access_another_users_paper(client, auth_headers, minimal_pdf_bytes):
    headers_a, _ = auth_headers
    headers_b = _register(client, "other-user@example.com")

    upload = client.post(
        "/api/papers",
        headers=headers_a,
        files={"file": ("paper.pdf", io.BytesIO(minimal_pdf_bytes), "application/pdf")},
    )
    assert upload.status_code == 201
    paper_id = upload.json()["id"]

    resp = client.get(f"/api/papers/{paper_id}", headers=headers_b)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "PAPER_NOT_FOUND"


def test_list_papers_only_returns_own_papers(client, auth_headers, minimal_pdf_bytes):
    headers_a, _ = auth_headers
    headers_b = _register(client, "second-user@example.com")

    client.post(
        "/api/papers", headers=headers_a, files={"file": ("a.pdf", io.BytesIO(minimal_pdf_bytes), "application/pdf")}
    )

    resp = client.get("/api/papers", headers=headers_b)
    assert resp.status_code == 200
    assert resp.json() == []


def test_delete_paper_requires_ownership(client, auth_headers, minimal_pdf_bytes):
    headers_a, _ = auth_headers
    headers_b = _register(client, "third-user@example.com")

    upload = client.post(
        "/api/papers", headers=headers_a, files={"file": ("a.pdf", io.BytesIO(minimal_pdf_bytes), "application/pdf")}
    )
    paper_id = upload.json()["id"]

    resp = client.delete(f"/api/papers/{paper_id}", headers=headers_b)
    assert resp.status_code == 404
