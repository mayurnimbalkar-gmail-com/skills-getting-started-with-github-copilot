import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Fixture to provide a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities between tests"""
    original = copy.deepcopy(activities)
    yield
    # Restore original state after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    def test_get_activities_returns_all(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity in expected_activities:
            assert activity in data

    def test_activity_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity_fields = set(data["Chess Club"].keys())
        
        # Assert
        assert response.status_code == 200
        assert required_fields.issubset(activity_fields)


class TestSignup:
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        # Arrange
        new_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup adds the participant to the activity list"""
        # Arrange
        new_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        initial_participant_count = len(activities[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        
        # Assert
        updated_participant_count = len(activities[activity_name]["participants"])
        assert updated_participant_count == initial_participant_count + 1
        assert new_email in activities[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        nonexistent_activity = "Fake Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregister:
    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes the participant from the activity list"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        updated_count = len(activities[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test unregister from non-existent activity returns 404"""
        # Arrange
        nonexistent_activity = "Fake Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{nonexistent_activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404

    def test_unregister_nonexistent_participant_returns_404(self, client, reset_activities):
        """Test unregister for a participant not in the activity returns 404"""
        # Arrange
        nonexistent_email = "notamember@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={nonexistent_email}")
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
