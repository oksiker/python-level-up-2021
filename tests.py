from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
    
def test_zad2():
    response = client.get("/method")
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}

    response = client.put("/method")
    assert response.status_code == 200
    assert response.json() == {"method": "PUT"}

    response = client.post("/method")
    assert response.status_code == 201
    assert response.json() == {"method": "POST"}

    response = client.delete("/method")
    assert response.status_code == 200
    assert response.json() == {"method": "DELETE"}

    response = client.options("/method")
    assert response.status_code == 200
    assert response.json() == {"method": "OPTIONS"}

