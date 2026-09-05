def test_register_creates_user_and_returns_token(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "SecurePass123", "full_name": "Alice"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["access_token"]


def test_register_rejects_duplicate_email(client):
    payload = {"email": "bob@example.com", "password": "SecurePass123"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "EMAIL_TAKEN"


def test_login_with_correct_credentials(client):
    client.post("/api/auth/register", json={"email": "carol@example.com", "password": "SecurePass123"})
    resp = client.post("/api/auth/login", json={"email": "carol@example.com", "password": "SecurePass123"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_with_wrong_password_returns_401(client):
    client.post("/api/auth/register", json={"email": "dave@example.com", "password": "SecurePass123"})
    resp = client.post("/api/auth/login", json={"email": "dave@example.com", "password": "WrongPassword"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_requires_authentication(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    headers, user = auth_headers
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == user["email"]
