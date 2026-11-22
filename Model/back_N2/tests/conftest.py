import pytest
from fastapi.testclient import TestClient

from back_n2.app import app


@pytest.fixture
def client():
    # O `with` dispara o lifespan, que carrega o modelo na inicialização.
    with TestClient(app) as test_client:
        yield test_client
