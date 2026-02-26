"""Tests for the data stats and sample endpoints."""


def test_data_stats(client):
    response = client.get("/api/v1/data/stats")
    assert response.status_code == 200
    data = response.json()
    assert "train" in data
    assert "dev" in data


def test_data_sample(client):
    response = client.get("/api/v1/data/sample?split=dev&n=2")
    # Returns 200 if data exists, 404 if not (DVC not pulled)
    assert response.status_code in (200, 404)


def test_data_sample_missing_split(client):
    response = client.get("/api/v1/data/sample?split=nonexistent&n=1")
    assert response.status_code == 404
