import pytest
from unittest.mock import patch, MagicMock
from app import app  # Import the Flask app


@pytest.fixture
def client():
    # Set up the Flask test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.locations.DatabaseManager')
def test_get_locations_success(mock_db_manager, client):
    # Mock database response
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_locations.return_value = [{"location": "location1"}, {"location": "location2"}]

    # Call the endpoint
    response = client.get("/locations")

    # Assert the expected response
    assert response.status_code == 200
    assert response.json == {"total_count": 2, "locations": [{"location": "location1"}, {"location": "location2"}]}


@patch('routes.locations.DatabaseManager')
def test_get_locations_success_with_active_servers(mock_db_manager, client):
    # Mock database response for active servers
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_locations.return_value = [{"location": "active1"}]

    # Call the endpoint with active_servers query param
    response = client.get("/locations?active_servers=true")

    # Assert the expected response
    assert response.status_code == 200
    assert response.json == {"total_count": 1, "locations": [{"location": "active1"}]}


@patch('routes.locations.DatabaseManager')
def test_get_locations_success_with_inactive_servers(mock_db_manager, client):
    # Mock database response for inactive servers
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_locations.return_value = [{"location": "inactive1"}]

    # Call the endpoint with active_servers query param set to false
    response = client.get("/locations?active_servers=false")

    # Assert the expected response
    assert response.status_code == 200
    assert response.json == {"total_count": 1, "locations": [{"location": "inactive1"}]}


@patch('routes.locations.DatabaseManager')
def test_get_locations_error_internal_error(mock_db_manager, client):
    # Mock the `get_locations` method to raise an exception
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_locations.side_effect = Exception("Database error")

    response = client.get("/locations")

    # Assert the expected error response
    assert response.status_code == 500
    assert response.json == {"error": "An unexpected error occurred", "details": "Database error"}
