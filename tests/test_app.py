import pytest
from src.app import activities

# GET /activities tests
def test_get_activities(client):
    # Arrange: No special setup needed, activities are reset by fixture

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status and response content
    assert response.status_code == 200
    assert response.json() == activities

# POST /activities/{activity_name}/signup tests
def test_signup_success(client):
    # Arrange: Choose an activity and a new email not already signed up
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Attempt to sign up
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check success and that email was added
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

def test_signup_duplicate(client):
    # Arrange: Choose an activity and an email already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act: Attempt to sign up again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check for 400 error and appropriate message
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_not_found(client):
    # Arrange: Choose a non-existent activity
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act: Attempt to sign up
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check for 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

@pytest.mark.xfail(reason="Capacity check not implemented in app")
def test_signup_capacity_full(client):
    # Arrange: Fill an activity to max capacity and try to add one more
    activity_name = "Basketball Team"  # max_participants: 15, currently 1 participant
    for i in range(14):  # Add 14 more to reach 15
        email = f"extra{i}@mergington.edu"
        activities[activity_name]["participants"].append(email)
    new_email = "overflow@mergington.edu"

    # Act: Attempt to sign up when at capacity
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert: Should fail due to capacity, but currently succeeds (xfail)
    assert response.status_code == 400
    assert "capacity" in response.json()["detail"].lower()

@pytest.mark.xfail(reason="Email validation not implemented in app")
def test_signup_invalid_email(client):
    # Arrange: Choose an activity and an invalid email
    activity_name = "Chess Club"
    invalid_email = ""

    # Act: Attempt to sign up with invalid email
    response = client.post(f"/activities/{activity_name}/signup", params={"email": invalid_email})

    # Assert: Should fail due to invalid email, but currently succeeds (xfail)
    assert response.status_code == 422  # Pydantic validation error

# POST /activities/{activity_name}/unregister tests
def test_unregister_success(client):
    # Arrange: Choose an activity and an email already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act: Attempt to unregister
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Check success and that email was removed
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

def test_unregister_not_registered(client):
    # Arrange: Choose an activity and an email not signed up
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act: Attempt to unregister
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Check for 400 error
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_unregister_not_found(client):
    # Arrange: Choose a non-existent activity
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act: Attempt to unregister
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Check for 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

@pytest.mark.xfail(reason="Email validation not implemented in app")
def test_unregister_invalid_email(client):
    # Arrange: Choose an activity and an invalid email
    activity_name = "Chess Club"
    invalid_email = ""

    # Act: Attempt to unregister with invalid email
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": invalid_email})

    # Assert: Should fail due to invalid email, but currently succeeds (xfail)
    assert response.status_code == 422

def test_unregister_then_resignup(client):
    # Arrange: Sign up, then unregister, then sign up again
    activity_name = "Chess Club"
    email = "resignup@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # Sign up first

    # Act: Unregister, then sign up again
    client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Re-signup should succeed
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]

# GET / tests
def test_root_redirect(client):
    # Arrange: No special setup needed

    # Act: Make GET request to root (don't follow redirects)
    response = client.get("/", follow_redirects=False)

    # Assert: Check for redirect to static file
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"