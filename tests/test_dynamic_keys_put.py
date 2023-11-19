import pytest
from unittest.mock import patch
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


def test_put_dynamic_keys_error_unauthorized_access(unauth_client):

    # Prepare data for POST request
    data = {"key": "value"}

    # Send POST request
    response = unauth_client.put("/keys/1", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 401


@patch('routes.dynamic_keys.DatabaseManager')
def test_put_dynamic_keys_success(mock_db_manager, auth_client):
    mock_db_instance = mock_db_manager.return_value
    key_id = 1
    new_outline_key_uuid = "new_uuid123"

    # Setup mock responses
    mock_db_instance.check_dynamic_key_exists_by_id.return_value = True
    mock_db_instance.check_outline_key_exists.return_value = True
    mock_db_instance.get_access_url_by_outline_key.return_value = "some_access_url"
    mock_db_instance.parse_access_url.return_value = {
        "server": "new_example.com",
        "server_port": 5678,
        "password": "new_password",
        "method": "new_method"
    }
    mock_db_instance.update_dynamic_key_with_new_outline_key.return_value = None

    # Prepare request data
    data = {"outline_key_uuid": new_outline_key_uuid}
    response = auth_client.put(f"/keys/{key_id}", data=json.dumps(data), content_type='application/json')

    # Assertions
    assert response.status_code == 200
    assert response.json == {"message": "Dynamic key and associated outline key updated successfully"}

    # Verify that the update method was called with the expected parameters
    mock_db_instance.update_dynamic_key_with_new_outline_key.assert_called_with(
        key_id, new_outline_key_uuid, mock_db_instance.parse_access_url.return_value
    )


@patch('routes.dynamic_keys.DatabaseManager')
def test_put_dynamic_keys_error_not_found(mock_db_manager, auth_client):
    mock_db_instance = mock_db_manager.return_value
    key_id = 1
    new_outline_key_uuid = "new_uuid123"

    # Setup mock response
    mock_db_instance.check_dynamic_key_exists_by_id.return_value = False

    # Prepare request data
    data = {"outline_key_uuid": new_outline_key_uuid}
    response = auth_client.put(f"/keys/{key_id}", data=json.dumps(data), content_type='application/json')

    # Assertions
    assert response.status_code == 404
    assert response.json == {"error": "Dynamic key not found"}


def test_put_dynamic_keys_error_invalid_param(auth_client):
    key_id = 1
    data = {"wrong_param": "some_value"}
    response = auth_client.put(f"/keys/{key_id}", data=json.dumps(data), content_type='application/json')

    # Assertions
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json['error'] == "Missing required parameter: 'outline_key_uuid'"


@patch('routes.dynamic_keys.DatabaseManager')
def test_put_dynamic_keys_error_internal_error(mock_db_manager, auth_client):
    mock_db_instance = mock_db_manager.return_value
    key_id = 1
    new_outline_key_uuid = "new_uuid123"

    # Simulate an exception during the update operation
    mock_db_instance.check_dynamic_key_exists_by_id.side_effect = Exception("Internal error")

    # Prepare request data
    data = {"outline_key_uuid": new_outline_key_uuid}
    response = auth_client.put(f"/keys/{key_id}", data=json.dumps(data), content_type='application/json')

    # Assertions
    assert response.status_code == 500
    assert "error" in response.json
    assert response.json['error'] == "An unexpected error occurred"
