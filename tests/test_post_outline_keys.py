import pytest
from unittest.mock import patch, MagicMock
from app import app  # Import the Flask app
import json
import requests


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.outline_keys.requests.post')
@patch('routes.outline_keys.requests.put')
@patch('routes.outline_keys.DatabaseManager')
def test_post_outline_keys_success_all_success(mock_db_manager, mock_put, mock_post, client):
    # Mock the database manager methods
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_id.return_value = True
    mock_db_instance.get_server_api_url.return_value = "http://example.com/api"
    mock_db_instance.generate_unique_uuid.side_effect = ["uuid1", "uuid2"]

    # Mock successful responses for POST (key creation) and PUT (setting name) requests
    mock_post.return_value = MagicMock(status_code=201, json=lambda: {"id": "key_id", "accessUrl": "url"})
    mock_put.return_value = MagicMock(status_code=204)

    # Prepare data for POST request
    data = {"outline_server_id": 1, "number_of_keys": 2}

    # Send POST request
    response = client.post("/outline_keys", data=json.dumps(data), content_type='application/json')

    # Assertions
    assert response.status_code == 201
    assert response.json == {
        "total_success": 2,
        "successful_keys": [{"uuid": "uuid1"}, {"uuid": "uuid2"}],
        "total_failed": 0,
        "failed_keys": []
    }


@patch('routes.outline_keys.requests.put')
@patch('routes.outline_keys.requests.post')
@patch('routes.outline_keys.DatabaseManager')
def test_post_outline_keys_success_partial_success(mock_db_manager, mock_post, mock_put, client):
    # Mock DatabaseManager methods
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_id.return_value = True
    mock_db_instance.get_server_api_url.return_value = "http://example.com/api"
    mock_db_instance.generate_unique_uuid.side_effect = ["uuid1", "uuid2"]

    # First key creation succeeds (POST and PUT), second key creation (POST) fails
    mock_post.side_effect = [
        MagicMock(status_code=201, json=lambda: {"id": "key_id1", "accessUrl": "url1"}),  # Successful key creation
        requests.exceptions.RequestException("Failed to create key")  # Failed key creation
    ]
    mock_put.return_value = MagicMock(status_code=204)  # Successful PUT request for the first key

    # Data for POST request
    data = {"outline_server_id": 1, "number_of_keys": 2}

    # Send POST request
    response = client.post("/outline_keys", data=json.dumps(data), content_type='application/json')

    # Assertions
    assert response.status_code == 207
    assert "total_success" in response.json and response.json["total_success"] == 1
    assert "total_failed" in response.json and response.json["total_failed"] == 1
    assert "successful_keys" in response.json and len(response.json["successful_keys"]) == 1
    assert "failed_keys" in response.json and len(response.json["failed_keys"]) == 1


def test_post_outline_keys_error_invalid_parameters(client):
    # Invalid parameter types (non-integer values)
    data = {"outline_server_id": "one", "number_of_keys": "two"}
    response = client.post("/outline_keys", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert response.json == {"error": "Both outline_server_id and number_of_keys must be integers"}


def test_post_outline_keys_error_number_of_keys_zero(client):
    # number_of_keys is zero
    data = {"outline_server_id": 1, "number_of_keys": 0}
    response = client.post("/outline_keys", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert response.json == {"error": "number_of_keys cannot be zero"}


@patch('routes.outline_keys.DatabaseManager')
def test_post_outline_keys_error_server_not_found(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_id.return_value = False

    data = {"outline_server_id": 1, "number_of_keys": 2}
    response = client.post("/outline_keys", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 404
    assert response.json == {"error": "Server not found"}


@patch('routes.outline_keys.DatabaseManager')
def test_post_outline_keys_error_internal_error(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_id.side_effect = Exception("Database error")

    data = {"outline_server_id": 1, "number_of_keys": 2}
    response = client.post("/outline_keys", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 500
    assert response.json == {"error": "An unexpected error occurred", "details": "Database error"}
