import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Welcome" in r.data


def test_home_shows_version(client):
    r = client.get("/")
    assert b"version" in r.data


def test_status_page(client):
    r = client.get("/status")
    assert r.status_code == 200
    assert b"Running" in r.data


def test_api_info(client):
    r = client.get("/api/info")
    assert r.status_code == 200
    data = r.get_json()
    assert data["name"] == "flask-cicd-app"
    assert "version" in data
    assert "message" in data


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_metrics(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"app_up 1" in r.data


def test_unknown_route_404(client):
    assert client.get("/does-not-exist").status_code == 404
