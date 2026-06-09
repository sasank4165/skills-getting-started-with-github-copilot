import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activities = set(app_module.activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    json_data = response.json()
    assert set(json_data.keys()) == expected_activities
    assert all("participants" in details for details in json_data.values())


def test_signup_adds_participant_to_activity():
    # Arrange
    activity = "Chess Club"
    email = "tester@example.com"
    path = f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='@.')}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in app_module.activities[activity]["participants"]


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]
    path = f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='@.')}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_participant_from_activity():
    # Arrange
    activity = "Chess Club"
    email = "delete-me@example.com"
    signup_path = f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='@.')}"
    client.post(signup_path)

    delete_path = f"/activities/{quote(activity, safe='')}/participants?email={quote(email, safe='@.')}"

    # Act
    response = client.delete(delete_path)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in app_module.activities[activity]["participants"]


def test_delete_nonexistent_participant_returns_not_found():
    # Arrange
    activity = "Chess Club"
    email = "ghost@example.com"
    delete_path = f"/activities/{quote(activity, safe='')}/participants?email={quote(email, safe='@.')}"

    # Act
    response = client.delete(delete_path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_invalid_activity_returns_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "tester@example.com"
    path = f"/activities/{quote(activity, safe='')}/signup?email={quote(email, safe='@.')}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# Reset the in-memory activities after each test to keep tests isolated
original_activities = copy.deepcopy(app_module.activities)


def teardown_function():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))
