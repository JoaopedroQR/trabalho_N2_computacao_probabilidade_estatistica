import csv
import json
from http import HTTPStatus
from pathlib import Path
from typing import get_args

import pytest

from back_n2.app import API_TO_MODEL_COLUMNS
from back_n2.schemas import VariablesInput

ARTIFACTS = Path(__file__).parent.parent / 'back_n2' / 'artifacts'
TEST_PREDICTIONS = Path(__file__).parent / 'data' / 'test_predictions.csv'
CONTRACT = json.loads((ARTIFACTS / 'contrato.json').read_text('utf-8'))
INT_FIELDS = ('cholesterol', 'fastingBS', 'restingBP')

HIGH_RISK = {
    'sTSlope': 'Flat',
    'cholesterol': 217,
    'fastingBS': 1,
    'restingECG': 'ST',
    'restingBP': 139,
    'sex': 'M',
    'exerciseAngina': 'Y',
    'chestPainType': 'ATA',
}

LOW_RISK = {
    'sTSlope': 'Up',
    'cholesterol': 200,
    'fastingBS': 0,
    'restingECG': 'Normal',
    'restingBP': 120,
    'sex': 'F',
    'exerciseAngina': 'N',
    'chestPainType': 'ATA',
}


def test_post_answer_high_risk(client):
    response = client.post('/answer/', json=HIGH_RISK)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'status': 'Presença de Doença Cardíaca',
        'risk_level': 'Alto Risco',
        'probability': 0.93,
    }


def test_post_answer_low_risk(client):
    response = client.post('/answer/', json=LOW_RISK)

    body = response.json()
    assert response.status_code == HTTPStatus.CREATED
    assert body['status'] == 'Resultado Normal'
    assert body['risk_level'] == 'Baixo Risco'
    assert 0 <= body['probability'] < 0.5  # noqa: PLR2004


def test_zero_cholesterol_and_bp_mean_not_measured(client):
    payload = {**HIGH_RISK, 'cholesterol': 0, 'restingBP': 0}

    response = client.post('/answer/', json=payload)

    assert response.status_code == HTTPStatus.CREATED


def test_removed_fields_are_ignored(client):
    payload = {**HIGH_RISK, 'age': 54, 'maxhr': 150, 'oldpeak': 1.5}

    response = client.post('/answer/', json=payload)

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('sTSlope', 'string'),
        ('fastingBS', 2),
        ('restingECG', 'abc'),
        ('sex', 'X'),
        ('exerciseAngina', 'maybe'),
        ('chestPainType', 'ZZ'),
        ('cholesterol', -1),
        ('restingBP', -1),
        ('cholesterol', 'alto'),
    ],
)
def test_invalid_values_are_rejected(client, field, value):
    response = client.post('/answer/', json={**HIGH_RISK, field: value})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['loc'] == ['body', field]


@pytest.mark.parametrize('field', list(HIGH_RISK))
def test_missing_field_is_rejected(client, field):
    payload = {k: v for k, v in HIGH_RISK.items() if k != field}

    response = client.post('/answer/', json=payload)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_api_matches_model_contract():
    """Schema e mapeamento da API devem acompanhar o contrato.json."""
    assert set(VariablesInput.model_fields) == set(CONTRACT['api_columns'])
    assert API_TO_MODEL_COLUMNS == CONTRACT['api_columns']

    for api_name, column in CONTRACT['api_columns'].items():
        if column in CONTRACT['categorias']:
            annotation = VariablesInput.model_fields[api_name].annotation
            assert set(get_args(annotation)) == set(
                CONTRACT['categorias'][column]
            )


def test_api_reproduces_notebook_test_predictions(client):
    """Mesmas 184 linhas de teste do Colab devem gerar as mesmas classes."""
    with TEST_PREDICTIONS.open(encoding='utf-8') as file:
        rows = list(csv.DictReader(file))

    assert rows
    for row in rows:
        payload = {
            api_name: row[column]
            for api_name, column in CONTRACT['api_columns'].items()
        }
        for field in INT_FIELDS:
            payload[field] = int(payload[field])

        response = client.post('/answer/', json=payload)

        expected = 'Alto Risco' if row['predicted'] == '1' else 'Baixo Risco'
        assert response.status_code == HTTPStatus.CREATED
        assert response.json()['risk_level'] == expected, row
