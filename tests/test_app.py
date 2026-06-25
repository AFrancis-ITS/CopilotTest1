import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset in-memory data after each test to keep tests independent."""
    original_state = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_state)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_all_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    existing_email = app_module.activities["Chess Club"]["participants"][0]

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email(client):
    # Arrange
    existing_email = app_module.activities["Chess Club"]["participants"][0]

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 200
    assert existing_email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_non_member_returns_404(client):
    # Arrange
    email = "nosuchstudent@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"