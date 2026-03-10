"""Unit tests for core business logic."""

import pytest


class TestParticipantValidation:
    """Tests for participant-related validation logic."""

    def test_duplicate_email_check(self, client):
        """Test that duplicate email detection works correctly."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        # Michael is already in Chess Club (baseline data)

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]

    def test_email_case_sensitive(self, client):
        """Test that email checks are case-sensitive."""
        # Arrange
        email_lowercase = "student@mergington.edu"
        email_uppercase = "STUDENT@MERGINGTON.EDU"
        activity = "Gym Class"

        # Act - Sign up with lowercase
        response1 = client.post(
            f"/activities/{activity}/signup?email={email_lowercase}"
        )
        # Act - Try to sign up with uppercase
        response2 = client.post(
            f"/activities/{activity}/signup?email={email_uppercase}"
        )

        # Assert
        # App treats emails as case-sensitive, so both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestActivityValidation:
    """Tests for activity-related validation logic."""

    def test_invalid_activity_returns_404(self, client):
        """Test that invalid activity name returns 404."""
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"].lower()

    def test_activity_names_case_sensitive(self, client):
        """Test that activity names are case-sensitive."""
        # Arrange
        activity_wrong_case = "chess club"  # lowercase, should not match "Chess Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_wrong_case}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404

    def test_activity_names_whitespace_sensitive(self, client):
        """Test that activity names are whitespace-sensitive."""
        # Arrange
        activity_extra_space = "Chess Club "  # with trailing space
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_extra_space}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404


class TestResponseMessages:
    """Tests for response message format and content."""

    def test_signup_response_format(self, client, sample_email):
        """Test that signup response message is properly formatted."""
        # Arrange
        activity = "Gym Class"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={sample_email}"
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert sample_email in data["message"]
        assert activity in data["message"]
        assert "Signed up" in data["message"]

    def test_unregister_response_format(self, client):
        """Test that unregister response message is properly formatted."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        assert "Unregistered" in data["message"]

    def test_error_response_has_detail_field(self, client):
        """Test that error responses include 'detail' field."""
        # Arrange
        invalid_activity = "Nonexistent"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert "detail" in data


class TestActivityDataStructure:
    """Tests for activity data structure integrity."""

    def test_activity_has_all_required_fields(self, client):
        """Test that every activity has required fields."""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"

    def test_participants_is_list(self, client):
        """Test that participants field is always a list."""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(
                activity_data["participants"], list
            ), f"{activity_name} participants should be a list"

    def test_max_participants_is_integer(self, client):
        """Test that max_participants is an integer."""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(
                activity_data["max_participants"], int
            ), f"{activity_name} max_participants should be an integer"
