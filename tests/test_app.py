import pytest

from app.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"College Event Management System" in response.data


def test_events_page(client):
    response = client.get("/events")

    assert response.status_code == 200
    assert b"Upcoming Events" in response.data


def test_register_page(client):
    response = client.get("/register/1")

    assert response.status_code == 200
    assert b"Event Registration" in response.data


def test_registration(client):
    response = client.post(
        "/register/1",
        data={
            "name": "Test Student",
            "email": "test@example.com",
            "department": "CSE"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Registration Successful" in response.data


def test_admin_page(client):
    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data


def test_status(client):
    response = client.get("/status")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["application"] == "College Event Management System"


def test_api_info(client):
    response = client.get("/api/info")

    assert response.status_code == 200

    data = response.get_json()

    assert data["application"] == "College Event Management System"
    assert "events" in data
    assert "registrations" in data