from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def test_activity_setup_and_teardown():
    # Setup a temporary activity for testing
    app_module.activities["Test Activity"] = {
        "description": "Testing activity",
        "schedule": "Now",
        "max_participants": 2,
        "participants": []
    }
    yield
    # Teardown
    app_module.activities.pop("Test Activity", None)


def test_get_activities_contains_test_activity():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Test Activity" in data


def test_signup_and_remove_participant():
    # Sign up a participant
    r = client.post("/activities/Test%20Activity/signup?email=test1@example.com")
    assert r.status_code == 200
    assert "Signed up test1@example.com for Test Activity" in r.json()["message"]
    assert "test1@example.com" in app_module.activities["Test Activity"]["participants"]

    # Remove that participant
    r = client.delete("/activities/Test%20Activity/participants?email=test1@example.com")
    assert r.status_code == 200
    assert "Removed test1@example.com from Test Activity" in r.json()["message"]
    assert "test1@example.com" not in app_module.activities["Test Activity"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    r = client.delete("/activities/Test%20Activity/participants?email=unknown@example.com")
    assert r.status_code == 404


def test_signup_duplicate_and_capacity():
    # Sign up a student
    r = client.post("/activities/Test%20Activity/signup?email=a@example.com")
    assert r.status_code == 200

    # Duplicate signup should fail
    r = client.post("/activities/Test%20Activity/signup?email=a@example.com")
    assert r.status_code == 400

    # Fill to capacity
    r = client.post("/activities/Test%20Activity/signup?email=b@example.com")
    assert r.status_code == 200

    # Now activity is full
    r = client.post("/activities/Test%20Activity/signup?email=c@example.com")
    assert r.status_code == 400
