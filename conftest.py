"""
Pytest configuration and fixtures for the Task Management API tests.
"""

import os
import pytest
import tempfile
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# Set test environment variables before importing the app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "false"

from main import app
from database import get_session
from models import Task


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine with in-memory SQLite."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_session):
    """Create a test client with dependency overrides."""
    def get_test_session():
        return test_session

    app.dependency_overrides[get_session] = get_test_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task description",
        "status": "pending"
    }


@pytest.fixture
def sample_task_with_due_date():
    """Sample task data with due date for testing."""
    return {
        "title": "Task with Due Date",
        "description": "This task has a due date",
        "status": "pending",
        "due_date": "2025-12-31T23:59:59"  # Future date
    }


@pytest.fixture
def multiple_tasks_data():
    """Multiple sample tasks for testing."""
    return [
        {
            "title": "First Task",
            "description": "First test task",
            "status": "pending"
        },
        {
            "title": "Second Task",
            "description": "Second test task",
            "status": "completed"
        },
        {
            "title": "Third Task",
            "description": "Third test task",
            "status": "pending",
            "due_date": "2025-12-31T23:59:59"  # Future date
        }
    ]


@pytest.fixture
def created_task(client, sample_task_data):
    """Create a task and return its data."""
    response = client.post("/tasks", json=sample_task_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_multiple_tasks(client, multiple_tasks_data):
    """Create multiple tasks and return their data."""
    created_tasks = []
    for task_data in multiple_tasks_data:
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        created_tasks.append(response.json())
    return created_tasks
