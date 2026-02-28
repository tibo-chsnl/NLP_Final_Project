def test_ask_question_success(client):
    payload = {
        "context": "The Louvre Museum is located in Paris, France.",
        "question": "Where is the Louvre Museum located?",
    }
    response = client.post("/api/v1/qa/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)


def test_ask_question_empty_context(client):
    payload = {"context": "", "question": "What is this?"}
    response = client.post("/api/v1/qa/ask", json=payload)
    assert response.status_code == 400


def test_ask_question_empty_question(client):
    payload = {"context": "Some context here.", "question": ""}
    response = client.post("/api/v1/qa/ask", json=payload)
    assert response.status_code == 400


def test_ask_question_missing_fields(client):
    response = client.post("/api/v1/qa/ask", json={})
    assert response.status_code == 422
