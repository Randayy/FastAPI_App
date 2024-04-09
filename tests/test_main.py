from .conftest import client

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == { 
            "status_code": 200,
            "detail": "ok",
            "result": "working"
            }
    