# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.di.dependencies import getOrchestratorService


class MockOrchestrator:
    """Mock orchestrator matching the async interface."""
    def __init__(self):
        self.process_resume_and_job = AsyncMock()


@pytest.fixture
def mock_orchestrator():
    """Provides a mock orchestrator for each test."""
    mock = MockOrchestrator()
    mock.process_resume_and_job = AsyncMock(return_value={"ats_score": 92})

    # Override DI
    app.dependency_overrides[getOrchestratorService] = lambda: mock
    yield mock
    # Reset DI after each test
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)
