from http import HTTPStatus

from fastapi.testclient import TestClient

from back_n2.app import app

client = TestClient(app)


# def test_root_return_hello_world(client):
#     response = client.get('/')

#     assert response.status_code == HTTPStatus.OK
#     assert response.json() == {'message': 'Olá Mundo!'}


def test_post_answers(client):
    response = client.post(
        '/answer/',
        json={
            'age': 0,
            'cholesterol': 0,
            'maxhr': 0,
            'oldpeak': 0,
            'chestPainType': 'string',
            'sTSlope': 'string',
            'exerciseAngina': 'string',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'age': 0,
        'cholesterol': 0,
        'maxhr': 0,
        'oldpeak': 0,
        'chestPainType': 'string',
        'sTSlope': 'string',
        'exerciseAngina': 'string',
    }

def read_status(client):
    response = client.get('/answer/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'yes'