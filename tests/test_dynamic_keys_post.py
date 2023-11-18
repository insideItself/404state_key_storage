import pytest
from unittest.mock import patch
from app import app
import json


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.dynamic_keys.DatabaseManager')
def test_post_dynamic_keys_success(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_outline_key_exists.return_value = True
    mock_db_instance.check_dynamic_key_exists_for_user.return_value = False
    mock_db_instance.generate_unique_dynamic_key_id.return_value = "000000001"
    mock_db_instance.get_access_url_by_outline_key.return_value = "some_access_url"
    mock_db_instance.parse_access_url.return_value = {
        "server": "example.com",
        "server_port": 1234,
        "password": "password",
        "method": "method"
    }

    # Mock the update operation as well
    mock_db_instance.insert_dynamic_key.side_effect = None  # No exception, simulating successful insert and update

    data = {"tg_user_id": 123, "outline_key_uuid": "uuid123"}
    response = client.post("/keys", data=json.dumps(data), content_type='application/json')

    assert response.status_code == 201
    assert response.json == {"id": "000000001"}

    # Verify that insert_dynamic_key was called, which includes the update operation
    mock_db_instance.insert_dynamic_key.assert_called()


@patch('routes.dynamic_keys.DatabaseManager')
def test_post_dynamic_keys_error_update_failure(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_outline_key_exists.return_value = True
    mock_db_instance.check_dynamic_key_exists_for_user.return_value = False
    mock_db_instance.generate_unique_dynamic_key_id.return_value = "000000001"
    mock_db_instance.get_access_url_by_outline_key.return_value = "some_access_url"
    mock_db_instance.parse_access_url.return_value = {
        "server": "example.com",
        "server_port": 1234,
        "password": "password",
        "method": "method"
    }

    # Simulate an exception during the update operation
    mock_db_instance.insert_dynamic_key.side_effect = Exception("Update failure")

    data = {"tg_user_id": 123, "outline_key_uuid": "uuid123"}
    response = client.post("/keys", data=json.dumps(data), content_type='application/json')

    assert response.status_code == 500
    assert "error" in response.json
    assert response.json['error'] == "An unexpected error occurred"


@pytest.mark.parametrize("missing_key", ["tg_user_id", "outline_key_uuid"])
def test_post_dynamic_keys_error_missing_param(client, missing_key):
    # Prepare data with one missing key
    data: dict = {
        "tg_user_id": 123,
        "outline_key_uuid": "uuid123"
    }
    data.pop(missing_key)

    # Send POST request
    response = client.post("/keys", data=json.dumps(data), content_type='application/json')

    # Assert the expected response
    assert response.status_code == 400
    assert response.json == {"error": f"Missing required parameters: {missing_key}"}


def test_post_dynamic_keys_error_missing_all_params(client):
    # Prepare data with one missing key
    data: dict = {
        "wrong_key": "wrong_value"
    }

    # Send POST request
    response = client.post("/keys", data=json.dumps(data), content_type='application/json')

    # Assert the expected response
    assert response.status_code == 400
    # Extract the error message
    error_message = response.json.get("error")

    # Check if all required parameters are mentioned in the error message
    for param in ["tg_user_id", "outline_key_uuid"]:
        assert param in error_message


@patch('routes.dynamic_keys.DatabaseManager')
def test_post_dynamic_keys_error_outline_key_not_found(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_outline_key_exists.return_value = False

    data = {"tg_user_id": 123, "outline_key_uuid": "uuid123"}
    response = client.post("/keys", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 404
    assert response.json == {"error": "Outline key uuid not found"}


@patch('routes.dynamic_keys.DatabaseManager')
def test_post_dynamic_keys_error_exists_for_user(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_outline_key_exists.return_value = True
    mock_db_instance.check_dynamic_key_exists_for_user.return_value = True

    data = {"tg_user_id": 123, "outline_key_uuid": "uuid123"}
    response = client.post("/keys", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 409
    assert response.json == {"error": "Dynamic key with provided tg_user_id already exists in database"}


@patch('routes.dynamic_keys.DatabaseManager')
def test_post_dynamic_keys_error_internal_error(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_outline_key_exists.side_effect = Exception("Internal error")

    data = {"tg_user_id": 123, "outline_key_uuid": "uuid123"}
    response = client.post("/keys", data=json.dumps(data), content_type='application/json')
    assert response.status_code == 500
    assert "error" in response.json
