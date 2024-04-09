import pytest
from fastapi.testclient import TestClient
from utils.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == { 
            "status_code": 200,
            "detail": "ok",
            "result": "working"
            }
    
if __name__ == "__main__":
    pytest.main()