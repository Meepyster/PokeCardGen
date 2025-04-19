from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get10Cards():
    """Simple Sample Test"""
    response = client.get("/get-10-cards")
    assert response.status_code == 200
    data = response.json()
    assert len(data["cards"]) == 10
