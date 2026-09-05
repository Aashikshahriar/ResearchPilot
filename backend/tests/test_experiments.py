def test_create_and_list_experiment(client, auth_headers):
    headers, _ = auth_headers
    resp = client.post(
        "/api/experiments",
        headers=headers,
        json={"name": "DP-WNMF Baseline", "model": "WNMF", "dataset": "MovieLens", "learning_rate": 0.01, "epochs": 10},
    )
    assert resp.status_code == 201
    experiment_id = resp.json()["id"]

    listing = client.get("/api/experiments", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    metric = client.post(
        f"/api/experiments/{experiment_id}/metrics", headers=headers, json={"name": "accuracy", "value": 0.87, "step": 1}
    )
    assert metric.status_code == 201

    metrics = client.get(f"/api/experiments/{experiment_id}/metrics", headers=headers)
    assert metrics.status_code == 200
    assert metrics.json()[0]["name"] == "accuracy"


def test_experiment_not_visible_to_other_users(client, auth_headers):
    headers, _ = auth_headers
    resp = client.post("/api/experiments", headers=headers, json={"name": "Private Experiment"})
    experiment_id = resp.json()["id"]

    other = client.post("/api/auth/register", json={"email": "exp-other@example.com", "password": "SecurePass123"})
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    resp = client.get(f"/api/experiments/{experiment_id}", headers=other_headers)
    assert resp.status_code == 404
