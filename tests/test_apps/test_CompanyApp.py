from fastapi.testclient import TestClient
from apps.CompanyApp import CompanyApp


client = TestClient(CompanyApp)

def test_list_no_limits():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['success']


def test_list_limits_hp():
    response = client.get('/', params={'offset': 11, 'limit': 10})
    assert response.status_code == 200
    assert response.json()['success']


def test_list_ok_limits():
    response = client.get('/', params={'offset': 0, 'limit': 10})
    assert response.status_code == 200
    assert response.json()['success']
