import pytest
from unittest.mock import patch
from app import app  # Import the Flask app
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


def test_patch_dynamic_keys_error_unauthorized_access(unauth_client):

    # Send POST request
    response = unauth_client.patch("/keys/1", content_type='application/json')
    assert response.status_code == 401


@patch('routes.dynamic_keys.DatabaseManager')
def test_patch_dynamic_keys_success(mock_db_manager, auth_client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_dynamic_key_exists_by_id.return_value = True
    mock_db_instance.deactivate_dynamic_key_and_outline_key.side_effect = None  # No exception

    response = auth_client.patch("/keys/1")

    assert response.status_code == 200
    assert response.json == {"message": "Dynamic key and associated outline key updated successfully"}

    # Verify that deactivate_dynamic_key_and_outline_key was called
    mock_db_instance.deactivate_dynamic_key_and_outline_key.assert_called_with(1)


@patch('routes.dynamic_keys.DatabaseManager')
def test_patch_dynamic_keys_error_not_found(mock_db_manager, auth_client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_dynamic_key_exists_by_id.return_value = False

    response = auth_client.patch("/keys/1")

    assert response.status_code == 404
    assert response.json == {"error": "Dynamic key not found"}


@patch('routes.dynamic_keys.DatabaseManager')
def test_patch_dynamic_keys_error_internal_error(mock_db_manager, auth_client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_dynamic_key_exists_by_id.side_effect = Exception("Internal error")

    response = auth_client.patch("/keys/1")

    assert response.status_code == 500
    assert "error" in response.json
    assert response.json['error'] == "An unexpected error occurred"
