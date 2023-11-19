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


@patch('routes.dynamic_keys.DatabaseManager')
def test_get_dynamic_key_success(mock_db_manager, unauth_client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_dynamic_key_details.return_value = {
        "server": "example.com",
        "server_port": 1234,
        "password": "password",
        "method": "method"
    }

    key_id = 1
    tg_user_id = 123
    response = unauth_client.get(f"/keys/{key_id}?tg_user_id={tg_user_id}")

    assert response.status_code == 200
    assert response.json == {
        "server": "example.com",
        "server_port": 1234,
        "password": "password",
        "method": "method"
    }
    mock_db_instance.get_dynamic_key_details.assert_called_with(key_id, tg_user_id)


def test_get_dynamic_key_error_missing_params(unauth_client):
    key_id = 1
    response = unauth_client.get(f"/keys/{key_id}")

    assert response.status_code == 400
    assert "error" in response.json


@patch('routes.dynamic_keys.DatabaseManager')
def test_get_dynamic_key_error_not_found(mock_db_manager, unauth_client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_dynamic_key_details.return_value = None

    key_id = 1
    tg_user_id = 123
    response = unauth_client.get(f"/keys/{key_id}?tg_user_id={tg_user_id}")

    assert response.status_code == 404
    assert "error" in response.json
    mock_db_instance.get_dynamic_key_details.assert_called_with(key_id, tg_user_id)


@patch('routes.dynamic_keys.DatabaseManager')
def test_get_dynamic_key_error_internal_error(mock_db_manager, unauth_client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_dynamic_key_details.side_effect = Exception("Internal error")

    key_id = 1
    tg_user_id = 123
    response = unauth_client.get(f"/keys/{key_id}?tg_user_id={tg_user_id}")

    assert response.status_code == 500
    assert "error" in response.json
    mock_db_instance.get_dynamic_key_details.assert_called_with(key_id, tg_user_id)
