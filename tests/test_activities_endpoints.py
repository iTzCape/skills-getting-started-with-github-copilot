"""
FastAPI endpoint tests for the High School Management System API.

This module contains comprehensive tests for all API endpoints using the
AAA (Arrange-Act-Assert) pattern:
  - Arrange: Set up test data and fixtures
  - Act: Call the endpoint
  - Assert: Verify response status, data, and side effects

Tests cover both happy paths (valid requests) and error cases
(invalid activity, missing parameters, capacity full, etc.).
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint (redirect)."""

    def test_root_redirects_to_index_html(self, client):
        """
        Test that GET / redirects to /static/index.html.
        
        Arrange: TestClient is ready
        Act: Send GET request to /
        Assert: Response status is 307 (temporary redirect) and location header points to index.html
        """
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all 9 activities.
        
        Arrange: TestClient is ready
        Act: Send GET request to /activities
        Assert: Response contains all activities with correct structure
        """
        # Arrange
        expected_activity_count = 9
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Swimming Club", "Art Studio", "Drama Club", "Debate Team", "Science Club"
        }
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        assert set(data.keys()) == expected_activities

    def test_get_activities_returns_activity_details(self, client):
        """
        Test that each activity has required fields.
        
        Arrange: TestClient is ready
        Act: Send GET request to /activities
        Assert: Each activity has description, schedule, max_participants, and participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_details in data.items():
            assert set(activity_details.keys()) == required_fields
            assert isinstance(activity_details["participants"], list)
            assert isinstance(activity_details["max_participants"], int)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid_email_and_activity(self, client, valid_activity, valid_email):
        """
        Test successful signup for a valid activity with a new email.
        
        Arrange: Valid activity and new email address
        Act: Send POST request to signup endpoint
        Assert: Response status is 200 and success message is returned
        """
        # Arrange
        email = valid_email
        activity = valid_activity
        
        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_invalid_activity_returns_404(self, client, invalid_activity, valid_email):
        """
        Test that signup for a non-existent activity returns 404.
        
        Arrange: Invalid activity name and valid email
        Act: Send POST request with invalid activity name
        Assert: Response status is 404 and error detail is returned
        """
        # Arrange
        email = valid_email
        activity = invalid_activity
        
        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"

    def test_signup_missing_email_parameter_returns_422(self, client, valid_activity):
        """
        Test that signup without email parameter returns 422 (validation error).
        
        Arrange: Valid activity but no email parameter
        Act: Send POST request without email query parameter
        Assert: Response status is 422 (unprocessable entity)
        """
        # Arrange
        activity = valid_activity
        
        # Act
        response = client.post(f"/activities/{activity}/signup")
        
        # Assert
        assert response.status_code == 422

    def test_signup_duplicate_email_returns_400(self, client, valid_activity, existing_email):
        """
        Test that duplicate signup attempt returns 400 (bad request).
        
        Arrange: Valid activity and email that already exists in participants
        Act: Send POST request with email already signed up
        Assert: Response status is 400 and error message indicates already signed up
        """
        # Arrange
        email = existing_email  # michael@mergington.edu is already in Chess Club
        activity = valid_activity  # Chess Club
        
        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert data["detail"] == "Already signed up for this activity"

    def test_signup_modifies_participants_list(self, client, valid_activity, valid_email):
        """
        Test that successful signup adds the email to the participants list.
        
        Arrange: Valid activity and new email
        Act: Sign up and then fetch activities to verify participant was added
        Assert: The new email appears in the activity's participants list
        """
        # Arrange
        email = valid_email
        activity = valid_activity
        
        # Act
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities_data[activity]["participants"]


class TestRemoveEndpoint:
    """Tests for the DELETE /activities/{activity_name}/remove endpoint."""

    def test_remove_existing_participant_succeeds(self, client, valid_activity, existing_email):
        """
        Test successful removal of an existing participant.
        
        Arrange: Valid activity and email that exists in participants
        Act: Send DELETE request to remove endpoint
        Assert: Response status is 200 and success message is returned
        """
        # Arrange
        email = existing_email  # michael@mergington.edu in Chess Club
        activity = valid_activity
        
        # Act
        response = client.delete(f"/activities/{activity}/remove", params={"email": email})
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_remove_invalid_activity_returns_404(self, client, invalid_activity, valid_email):
        """
        Test that removal from non-existent activity returns 404.
        
        Arrange: Invalid activity name
        Act: Send DELETE request with invalid activity
        Assert: Response status is 404 and error detail is returned
        """
        # Arrange
        email = valid_email
        activity = invalid_activity
        
        # Act
        response = client.delete(f"/activities/{activity}/remove", params={"email": email})
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"

    def test_remove_missing_email_parameter_returns_422(self, client, valid_activity):
        """
        Test that removal without email parameter returns 422 (validation error).
        
        Arrange: Valid activity but no email parameter
        Act: Send DELETE request without email query parameter
        Assert: Response status is 422 (unprocessable entity)
        """
        # Arrange
        activity = valid_activity
        
        # Act
        response = client.delete(f"/activities/{activity}/remove")
        
        # Assert
        assert response.status_code == 422

    def test_remove_nonexistent_participant_returns_400(self, client, valid_activity, valid_email):
        """
        Test that removing a non-existent participant returns 400 (bad request).
        
        Arrange: Valid activity but email not in participants list
        Act: Send DELETE request with email not in activity
        Assert: Response status is 400 and error message indicates participant not found
        """
        # Arrange
        email = valid_email  # Email not yet signed up
        activity = valid_activity
        
        # Act
        response = client.delete(f"/activities/{activity}/remove", params={"email": email})
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert data["detail"] == "Participant not found in this activity"

    def test_remove_modifies_participants_list(self, client, valid_activity, existing_email):
        """
        Test that successful removal deletes the email from the participants list.
        
        Arrange: Valid activity and email that exists in participants
        Act: Remove participant and then fetch activities to verify removal
        Assert: The email no longer appears in the activity's participants list
        """
        # Arrange
        email = existing_email
        activity = valid_activity
        
        # Act
        remove_response = client.delete(f"/activities/{activity}/remove", params={"email": email})
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Assert
        assert remove_response.status_code == 200
        assert email not in activities_data[activity]["participants"]
