"""
Tests for the Mergington High School Activities API endpoints
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check that all expected activities are present
        expected_activities = [
            "Soccer Team", "Basketball Club", "Art Club", "Drama Society",
            "Math Olympiad", "Science Club", "Chess Club", "Programming Class", "Gym Class"
        ]
        for activity_name in expected_activities:
            assert activity_name in activities
    
    def test_activities_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_soccer_team_specific_data(self, client, reset_activities):
        """Test specific data for Soccer Team activity"""
        response = client.get("/activities")
        activities = response.json()
        
        soccer_team = activities["Soccer Team"]
        assert soccer_team["max_participants"] == 18
        assert "lucas@mergington.edu" in soccer_team["participants"]
        assert "mia@mergington.edu" in soccer_team["participants"]
        assert len(soccer_team["participants"]) == 2


class TestSignupEndpoint:
    """Tests for the activity signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Soccer Team"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity in result["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]
    
    def test_duplicate_signup(self, client, reset_activities):
        """Test duplicate signup for the same activity"""
        email = "lucas@mergington.edu"  # Already signed up for Soccer Team
        activity = "Soccer Team"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]
    
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email"""
        email = "student-test@mergington.edu"  # Use hyphen instead of plus
        activity = "Art Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]
    
    def test_signup_url_encoding(self, client, reset_activities):
        """Test signup with URL-encoded parameters"""
        email = "test@mergington.edu"
        activity = "Programming Class"
        
        # Use URL encoding
        encoded_email = "test%40mergington.edu"
        encoded_activity = "Programming%20Class"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={encoded_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the participant was added with the decoded email
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]
    
    def test_signup_with_plus_sign_in_email(self, client, reset_activities):
        """Test signup with plus sign in email (URL encoded properly)"""
        original_email = "student+test@mergington.edu"
        activity = "Science Club"
        
        # Properly URL encode the plus sign as %2B
        encoded_email = "student%2Btest@mergington.edu"
        
        response = client.post(f"/activities/{activity}/signup?email={encoded_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the participant was added with the original email
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert original_email in activities[activity]["participants"]


class TestUnregisterEndpoint:
    """Tests for the activity unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        email = "lucas@mergington.edu"  # Already signed up for Soccer Team
        activity = "Soccer Team"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity in result["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from a non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]
    
    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregistration when not signed up for the activity"""
        email = "notsignedup@mergington.edu"
        activity = "Soccer Team"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"]
    
    def test_unregister_url_encoding(self, client, reset_activities):
        """Test unregistration with URL-encoded parameters"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"
        
        # Use URL encoding
        encoded_email = "michael%40mergington.edu"
        encoded_activity = "Chess%20Club"
        
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={encoded_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete signup and unregister flow"""
        email = "flowtest@mergington.edu"
        activity = "Drama Society"
        
        # Initial state - user not signed up
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]
        initial_count = len(activities[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count
    
    def test_multiple_activities_signup(self, client, reset_activities):
        """Test signing up for multiple activities"""
        email = "multisignup@mergington.edu"
        activities_to_join = ["Art Club", "Science Club", "Chess Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify user is signed up for all activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for activity in activities_to_join:
            assert email in activities[activity]["participants"]
    
    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that participant counts are correctly tracked"""
        activity = "Math Olympiad"
        
        # Get initial state
        activities_response = client.get("/activities")
        activities = activities_response.json()
        initial_participants = len(activities[activity]["participants"])
        max_participants = activities[activity]["max_participants"]
        
        # Add a new participant
        new_email = "capacity@mergington.edu"
        signup_response = client.post(f"/activities/{activity}/signup?email={new_email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify participant count increased
        activities_response = client.get("/activities")
        activities = activities_response.json()
        new_participants = len(activities[activity]["participants"])
        assert new_participants == initial_participants + 1
        assert new_participants <= max_participants
        
        # Calculate spots left
        spots_left = max_participants - new_participants
        assert spots_left >= 0