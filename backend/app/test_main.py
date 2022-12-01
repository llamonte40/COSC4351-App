from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/user/register",
    json=
    {
    "email": "test@test.com",
    "password": "test",
    "address_type": "mail",
    "address": "test test",
    "fav_dinner": "test meal",
    "point": 0,
    "fav_payment": "test card"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "success"
def test_login_user():
    response = client.post(
        "/user/login",
        json={"email": "test@test.com", "password": "test"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "success",
    }

def test_invalid_login_user():
    response = client.post(
        "/user/login",
        json={"email": "wrong_test@test.com", "password": "test"},
    )
    assert response.status_code != 200
    assert response.json() == {
        "detail": {
            "message": "Wrong Username or Password."
        }
    }

def test_get_all_users():
    response = client.get("/user/list")
    assert response.status_code == 200

def test_remove_user():
    response = client.put("/user/delete",
    json={"email": "test@test.com", "password": "test"})
    assert response.status_code == 200
    assert response.json() == {
        "message": "success",
    }

def test_reservation():
    response = client.post("/reservation",
    json={
    "email": "test@test.com",
    "name": "test user",
    "phone_no": "test no123",
    "time": "2022-12-01",
    "hour": 12,
    "guest": 3,
    "tables": [
        "A1","A2"
    ]
    })
    assert response.status_code == 200
    assert response.json()["message"] == "success"


def test_invalid_reservation():
    response = client.post("/reservation",
    json={
    "email": "test@test.com",
    "name": "test user",
    "phone_no": "test no123",
    "time": "2022-12-01",
    "hour": 12,
    "guest": 3,
    "tables": [
        "A1","A2"
    ]
    })
    assert response.status_code != 200
    assert response.json() == {
        "detail": {
            "message": "selected tables are not available."
        }
    }

def test_cancel_reservation():
    response = client.delete("/reservation/delete/test@test.com")
    assert response.status_code == 200
    assert response.json() == {
        "message": "success",
    }

