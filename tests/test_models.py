"""
Unit tests for Task model validation and functionality.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from models import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority


@pytest.mark.unit
class TestTaskModel:
    """Test class for Task model validation."""

    def test_task_create_valid_minimal(self):
        """Test creating a task with minimal valid data."""
        task = TaskCreate(title="Test Task")
        
        assert task.title == "Test Task"
        assert task.status == TaskStatus.pending  # Default
        assert task.priority == TaskPriority.medium  # Default
        assert task.description is None
        assert task.due_date is None
        assert task.assigned_to is None

    def test_task_create_valid_complete(self):
        """Test creating a task with all valid fields."""
        due_date = datetime(2026, 12, 31, 23, 59, 59)
        task = TaskCreate(
            title="Complete Task",
            description="Full description",
            status=TaskStatus.in_progress,
            priority=TaskPriority.high,
            due_date=due_date,
            assigned_to="John Doe"
        )
        
        assert task.title == "Complete Task"
        assert task.status == TaskStatus.in_progress
        assert task.priority == TaskPriority.high
        assert task.due_date == due_date
        assert task.assigned_to == "John Doe"

    # Title validation tests (required by task.md)
    def test_title_validation_errors(self):
        """Test title validation: empty, whitespace, and length."""
        # Empty title
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")
        assert "empty" in exc_info.value.errors()[0]["msg"].lower()
        
        # Whitespace-only title  
        with pytest.raises(ValidationError):
            TaskCreate(title="   ")
            
        # Too long title (over 200 chars)
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="x" * 201)
        assert exc_info.value.errors()[0]["type"] == "string_too_long"

    # Due date validation (required by task.md)
    def test_due_date_validation(self):
        """Test due date must be in future."""
        past_date = datetime(2020, 1, 1)
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test", due_date=past_date)
        assert "future" in exc_info.value.errors()[0]["msg"].lower()

    # Field length validation
    def test_field_length_validation(self):
        """Test field length constraints."""
        # Description too long (over 1000 chars)
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test", description="x" * 1001)
        assert exc_info.value.errors()[0]["type"] == "string_too_long"
        
        # Assigned_to too long (over 100 chars)  
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test", assigned_to="x" * 101)
        assert exc_info.value.errors()[0]["type"] == "string_too_long"

    def test_task_update_model(self):
        """Test TaskUpdate with partial and complete data."""
        # Partial update
        update = TaskUpdate(status=TaskStatus.completed)
        assert update.status == TaskStatus.completed
        assert update.title is None
        
        # Complete update
        due_date = datetime(2026, 12, 31)
        update = TaskUpdate(
            title="Updated",
            status=TaskStatus.completed,
            priority=TaskPriority.urgent,
            due_date=due_date
        )
        assert update.title == "Updated"
        assert update.status == TaskStatus.completed
        assert update.due_date == due_date

    def test_task_model_with_timestamps(self):
        """Test Task model includes proper timestamps."""
        task = Task(title="Test Task")
        
        assert task.created_at is not None
        assert task.updated_at is None  # Default for new tasks
        assert isinstance(task.created_at, datetime)
