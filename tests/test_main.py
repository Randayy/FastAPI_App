from fastapi.testclient import TestClient
from App.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == { 
            "status_code": 200,
            "detail": "ok",
            "result": "working"
            }