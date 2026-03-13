import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Save a copy of the original in-memory activities so we can reset later
ORIGINAL_ACTIVITIES = {**activities}

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update({**ORIGINAL_ACTIVITIES})
    yield

client = TestClient(app)

def test_get_activities():
    # Arrange (state reset via fixture)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

def test_signup_duplicate_returns_400():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}

def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

def test_unregister_not_signed_returns_400():
    # Arrange
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not signed up for this activity"}