import pytest
from http import HTTPStatus

def test_server_is_up_and_running(client):
    """Test if the server is running"""
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data['status'] == 'service is running'

def test_get_filemanager(client):
    """Test get file manager entries"""
    response = client.get('api/v1/filemanager/')
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'message' in data

def test_get_filemanager_pagination(client):
    """Test get file manager entries with pagination"""
    response = client.get('/api/v1/filemanager/?page=1&per_page=1')
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'message' in data


# def test_validate_name_success(client):
#     """Test name validation - success case"""
#     response = client.post('/validate', json={'name': 'valid_file.txt'})
#     assert response.status_code == HTTPStatus.OK
#     data = response.get_json()
#     assert data['status'] == 'success'
#     assert data['message'] == 'Name is valid'
#
#
# def test_validate_name_invalid(client):
#     """Test name validation - invalid case"""
#     response = client.post('/validate', json={'name': ''})
#     assert response.status_code == HTTPStatus.BAD_REQUEST
#     data = response.get_json()
#     assert data['status'] == 'error'
#     assert data['message'] == 'Name is invalid'