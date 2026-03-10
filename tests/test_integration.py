"""Integration tests for FastAPI endpoints."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_contains_required_fields(self, client):
        """Test that activities contain all required fields."""
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]

        # Assert
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_shows_correct_participants(self, client):
        """Test that activities show correct participant list."""
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_participants = data["Chess Club"]["participants"]

        # Assert
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        assert len(chess_participants) == 2


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, sample_email):
        """Test successful signup for an activity."""
        # Act
        response = client.post(
            f"/activities/Gym Class/signup?email={sample_email}",
            follow_redirects=False
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert sample_email in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_email):
        """Test that signup actually adds participant to activity list."""
        # Arrange
        activity_name = "Gym Class"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={sample_email}")
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]

        # Assert
        assert sample_email in participants

    def test_signup_activity_not_found(self, client, sample_email):
        """Test signup fails when activity doesn't exist."""
        # Arrange
        invalid_activity = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={sample_email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_fails(self, client):
        """Test that signing up twice fails."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act (user already signed up)
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]

    def test_signup_different_activities_allowed(self, client, sample_email):
        """Test that same student can sign up for multiple activities."""
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Gym Class"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup?email={sample_email}"
        )
        response2 = client.post(
            f"/activities/{activity2}/signup?email={sample_email}"
        )
        activities = client.get("/activities").json()

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert sample_email in activities[activity1]["participants"]
        assert sample_email in activities[activity2]["participants"]

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can sign up for same activity."""
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity = "Programming Class"

        # Act
        response1 = client.post(
            f"/activities/{activity}/signup?email={email1}"
        )
        response2 = client.post(
            f"/activities/{activity}/signup?email={email2}"
        )
        activities = client.get("/activities").json()
        participants = activities[activity]["participants"]

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in participants
        assert email2 in participants


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregistration from activity."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from list."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Verify baseline: participant exists
        activities_before = client.get("/activities").json()
        assert email in activities_before[activity]["participants"]

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")
        activities_after = client.get("/activities").json()

        # Assert
        assert email not in activities_after[activity]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister fails when activity doesn't exist."""
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_signed_up(self, client):
        """Test unregister fails when student isn't signed up."""
        # Arrange
        email = "unknown@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert "not signed up" in data["detail"]

    def test_unregister_then_signup_again(self, client, sample_email):
        """Test that student can sign up again after unregistering."""
        # Arrange
        activity = "Gym Class"

        # Act - Sign up
        response1 = client.post(
            f"/activities/{activity}/signup?email={sample_email}"
        )
        # Act - Unregister
        response2 = client.delete(
            f"/activities/{activity}/signup?email={sample_email}"
        )
        # Act - Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup?email={sample_email}"
        )
        activities = client.get("/activities").json()

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert sample_email in activities[activity]["participants"]


class TestDataConsistency:
    """Tests for data consistency across operations."""

    def test_participant_count_accurate_after_signup(self, client, sample_email):
        """Test that participant count is accurate after signup."""
        # Arrange
        activity = "Gym Class"
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity]["participants"])

        # Act
        client.post(f"/activities/{activity}/signup?email={sample_email}")
        activities_after = client.get("/activities").json()
        new_count = len(activities_after[activity]["participants"])

        # Assert
        assert new_count == initial_count + 1

    def test_participant_count_accurate_after_unregister(self, client):
        """Test that participant count is accurate after unregister."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity]["participants"])

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")
        activities_after = client.get("/activities").json()
        new_count = len(activities_after[activity]["participants"])

        # Assert
        assert new_count == initial_count - 1

    def test_other_activities_unaffected_by_signup(self, client, sample_email):
        """Test that signing up to one activity doesn't affect others."""
        # Arrange
        activities_initial = client.get("/activities").json()
        initial_gym_count = len(activities_initial["Gym Class"]["participants"])
        initial_chess_count = len(activities_initial["Chess Club"]["participants"])

        # Act
        client.post(
            f"/activities/Programming Class/signup?email={sample_email}"
        )
        activities_final = client.get("/activities").json()

        # Assert
        assert len(activities_final["Gym Class"]["participants"]) == initial_gym_count
        assert len(activities_final["Chess Club"]["participants"]) == initial_chess_count
