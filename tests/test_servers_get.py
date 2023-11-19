import pytest
from unittest.mock import patch
from app import app
import base64
from config import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD


@pytest.fixture
def auth_client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        # Encode credentials
        credentials = base64.b64encode(f"{BASIC_AUTH_USERNAME}:{BASIC_AUTH_PASSWORD}".encode()).decode('utf-8')
        # Set the Authorization header for all requests
        test_client.environ_base['HTTP_AUTHORIZATION'] = 'Basic ' + credentials
        yield test_client


@pytest.fixture
def unauth_client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        # No Authorization header
        yield test_client


def test_get_servers_error_unauthorized_access(unauth_client):

    response = unauth_client.get("/servers")
    assert response.status_code == 401


@patch('routes.servers.DatabaseManager')
def test_get_servers_success(mock_db_manager, auth_client):

    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_servers.return_value = {
        "total_count": 2,
        "servers": [
            {"id": 1, "location": "test_location1", "unused_keys": 2},
            {"id": 2, "location": "test_location2", "unused_keys": 0}
        ]
    }

    # Call the endpoint
    response = auth_client.get("/servers")

    # Assert the expected response
    assert response.status_code == 200
    assert response.json == {
        "total_count": 2,
        "servers": [
            {"id": 1, "location": "test_location1", "unused_keys": 2},
            {"id": 2, "location": "test_location2", "unused_keys": 0}
        ]
    }


@patch('routes.servers.DatabaseManager')
def test_get_servers_error_location_not_found(mock_db_manager, auth_client):

    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.location_exists.return_value = False

    # Call the endpoint
    response = auth_client.get("/servers?location=non_existent_location")

    # Assert the expected response
    assert response.status_code == 404
    assert response.json == {"error": "Location not found"}


@patch('routes.servers.DatabaseManager')
def test_get_servers_error_internal_error(mock_db_manager, auth_client):
    # Mock the `get_servers` method to raise an exception
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_servers.side_effect = Exception("Database error")

    response = auth_client.get("/servers")

    assert response.status_code == 500
    assert response.json == {"error": "An unexpected error occurred", "details": "Database error"}
