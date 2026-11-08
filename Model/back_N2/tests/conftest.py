import pytest
from fastapi.testclient import TestClient

from back_n2.app import app


@pytest.fixture
def client():
    return TestClient(app)
