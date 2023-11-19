import pytest
from unittest.mock import patch, MagicMock
from app import app
import json
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


def test_post_outline_keys_error_unauthorized_access(unauth_client):

    # Prepare data for POST request
    data = {"key": "value"}

    # Send POST request
    response = unauth_client.post("/servers", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 401


@patch('routes.servers.requests.get')
@patch('routes.servers.DatabaseManager')
def test_post_servers_success(mock_db_manager, mock_get, auth_client):
    # Mock the external API request with a successful response
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {
        "hostnameForAccessKeys": "test-hostname", "portForNewAccessKeys": 1234
    })

    # Mock the database manager to simulate successful creation
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_api_url.return_value = False  # Explicitly mock to return False
    mock_db_instance.create_outline_server.return_value = 1

    data = {
        "api_url": "http://example.com/api",
        "location": "example_location",
        "provider_id": 1
    }

    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    assert "id" in response.json


@pytest.mark.parametrize("missing_key", ["api_url", "location", "provider_id"])
def test_post_servers_error_missing_param(auth_client, missing_key):
    # Prepare data with one missing key
    data: dict = {
        "api_url": "http://example.com/api",
        "location": "example_location",
        "provider_id": 1
    }
    data.pop(missing_key)

    # Send POST request
    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')

    # Assert the expected response
    assert response.status_code == 400
    assert response.json == {"error": f"Missing required parameters: {missing_key}"}


def test_post_servers_error_missing_all_params(auth_client):

    data: dict = {
        "wrong_key": "wrong_value"
    }

    # Send POST request
    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')

    # Assert the expected response
    assert response.status_code == 400
    # Extract the error message
    error_message = response.json.get("error")

    # Check if all required parameters are mentioned in the error message
    for param in ["api_url", "provider_id", "location"]:
        assert param in error_message


@pytest.mark.parametrize("invalid_provider_id", [-1, 0, "string", 1.5])
def test_post_servers_error_invalid_provider_id_type(auth_client, invalid_provider_id):

    data: dict = {
        "api_url": "http://example.com/api",
        "location": "example_location",
        "provider_id": invalid_provider_id
    }

    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')

    assert response.status_code == 404
    assert response.json == {"error": "Invalid provider_id. It must be a positive integer"}


@pytest.mark.parametrize("invalid_scheme", ["ftp://example.com/api", "file:///path/to/file"])
def test_post_servers_error_invalid_api_url_scheme(auth_client, invalid_scheme):
    data = {
        "api_url": invalid_scheme,
        "location": "example_location",
        "provider_id": 1
    }

    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')

    assert response.status_code == 422
    assert response.json == {"error": "Invalid URL scheme"}


@patch('routes.servers.requests.get')
@patch('routes.servers.DatabaseManager')
def test_post_servers_error_duplicate_api_url(mock_db_manager, mock_get, auth_client):

    # Mock the external API request with a successful response
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {
        "hostnameForAccessKeys": "test-hostname", "portForNewAccessKeys": 1234
    })

    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_api_url.return_value = True

    data = {
        "api_url": "http://example.com/api",
        "location": "example_location",
        "provider_id": 1
    }

    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 409
    assert response.json == {"error": "Server with provided api_url already exists in database"}


@patch('routes.servers.requests.get')
def test_post_servers_error_external_request_error(mock_get, auth_client):

    mock_get.return_value = MagicMock(status_code=404)

    data = {
        "api_url": "http://example.com/api",
        "location": "example_location",
        "provider_id": 1
    }

    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 404
    assert response.json == {"error": "Server was found but unexpected error occurred"}


@patch('routes.servers.requests.get')
@patch('routes.servers.DatabaseManager')
def test_post_servers_error_db_creation_error(mock_db_manager, mock_get, auth_client):

    # Mock the external API request with a successful response
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {
        "hostnameForAccessKeys": "test-hostname", "portForNewAccessKeys": 1234
    })

    # Mock the database manager to simulate successful creation
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_api_url.return_value = False  # Explicitly mock to return False
    mock_db_instance.create_outline_server.side_effect = Exception("DB error")

    data = {
        "api_url": "http://example.com/api",
        "location": "example_location",
        "provider_id": 1
    }

    response = auth_client.post("/servers", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 500
    assert response.json == {"error": "Failed to create outline server", "details": "DB error"}
