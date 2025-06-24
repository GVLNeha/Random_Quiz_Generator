from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_quiz_success():
    response = client.post("/generate-quiz/", json={
        "topic": "Python",
        "num_questions": 5,
        "difficulty": "easy"
    })
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) == 5

def test_generate_quiz_invalid_topic():
    response = client.post("/generate-quiz/", json={
        "topic": "asdfghjkl",
        "num_questions": 5,
        "difficulty": "medium"
    })
    assert response.status_code == 400
    assert "error" in response.json()

def test_generate_quiz_empty_topic():
    response = client.post("/generate-quiz/", json={
        "topic": "",
        "num_questions": 5,
        "difficulty": "medium"
    })
    assert response.status_code == 400
    assert "error" in response.json()

def test_generate_quiz_invalid_num_questions():
    response = client.post("/generate-quiz/", json={
        "topic": "Math",
        "num_questions": -10,
        "difficulty": "hard"
    })
    assert response.status_code == 400
    assert "error" in response.json()

def test_generate_quiz_exceeds_max_questions():
    response = client.post("/generate-quiz/", json={
        "topic": "Science",
        "num_questions": 100,
        "difficulty": "medium"
    })
    assert response.status_code == 400
    assert "error" in response.json()

def test_generate_quiz_exceeds_max_characters_per_topic():
    long_topic = "A" * 101
    response = client.post("/generate-quiz/", json={
        "topic": long_topic,
        "num_questions": 10,
        "difficulty": "medium"
    })
    assert response.status_code == 400
    assert "error" in response.json()
