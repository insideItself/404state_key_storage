import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    # set up the Flask test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.servers.DatabaseManager')
def test_get_servers_success(mock_db_manager, client):

    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_servers.return_value = {
        "total_count": 2,
        "servers": [
            {"id": 1, "location": "test_location1", "unused_keys": 2},
            {"id": 2, "location": "test_location2", "unused_keys": 0}
        ]
    }

    # Call the endpoint
    response = client.get("/servers")

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
def test_get_servers_error_location_not_found(mock_db_manager, client):

    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.location_exists.return_value = False

    # Call the endpoint
    response = client.get("/servers?location=non_existent_location")

    # Assert the expected response
    assert response.status_code == 404
    assert response.json == {"error": "Location not found"}


@patch('routes.servers.DatabaseManager')
def test_get_servers_error_internal_error(mock_db_manager, client):
    # Mock the `get_servers` method to raise an exception
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_servers.side_effect = Exception("Database error")

    response = client.get("/servers")

    assert response.status_code == 500
    assert response.json == {"error": "An unexpected error occurred", "details": "Database error"}
