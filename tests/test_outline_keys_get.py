import pytest
from unittest.mock import patch
from app import app  # Import the Flask app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.outline_keys.DatabaseManager')
def test_get_outline_keys_success(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_outline_keys.return_value = [{"uuid": "uuid1", "access_url": "url1", "currently_used": True}]

    response = client.get("/outline_keys/1")
    assert response.status_code == 200
    assert response.json == {"total_count": 1,
                             "keys": [{"uuid": "uuid1", "access_url": "url1", "currently_used": True}]}


@patch('routes.outline_keys.DatabaseManager')
def test_get_outline_keys_success_filtered_by_currently_used(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_outline_keys.return_value = [{"uuid": "uuid1", "access_url": "url1", "currently_used": False}]

    response = client.get("/outline_keys/1?currently_used=false")
    assert response.status_code == 200
    assert response.json == {"total_count": 1,
                             "keys": [{"uuid": "uuid1", "access_url": "url1", "currently_used": False}]}


@patch('routes.outline_keys.DatabaseManager')
def test_get_outline_keys_success_with_limit(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_outline_keys.return_value = [{"uuid": "uuid1", "access_url": "url1", "currently_used": True}]

    response = client.get("/outline_keys/1?limit=1")
    assert response.status_code == 200
    assert response.json == {"total_count": 1,
                             "keys": [{"uuid": "uuid1", "access_url": "url1", "currently_used": True}]}


def test_get_outline_keys_error_invalid_currently_used_param(client):

    response = client.get("/outline_keys/1?currently_used=invalid")
    assert response.status_code == 400
    assert response.json == {"error": "Invalid 'currently_used' parameter. It must be 'true' or 'false'."}


def test_get_outline_keys_error_invalid_limit_param(client):
    response = client.get("/outline_keys/1?limit=invalid")
    assert response.status_code == 400
    assert response.json == {"error": "Invalid 'limit' parameter. It must be a positive integer."}


@patch('routes.outline_keys.DatabaseManager')
def test_get_outline_keys_error_server_not_found(mock_db_manager, client):

    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.check_server_exists_using_id.return_value = False

    response = client.get("/outline_keys/1")
    assert response.status_code == 404
    assert response.json == {"error": "Server not found"}


@patch('routes.outline_keys.DatabaseManager')
def test_get_outline_keys_error_internal_error(mock_db_manager, client):
    mock_db_instance = mock_db_manager.return_value
    mock_db_instance.get_outline_keys.side_effect = Exception("Database error")

    response = client.get("/outline_keys/1")
    assert response.status_code == 500
    assert response.json == {"error": "An unexpected error occurred", "details": "Database error"}
