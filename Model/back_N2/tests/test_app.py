from http import HTTPStatus

from fastapi.testclient import TestClient

from back_n2.app import app

client = TestClient(app)


def test_root_return_hello_world():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}
