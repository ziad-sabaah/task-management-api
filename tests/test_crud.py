"""
Unit tests for CRUD operations.
"""

import pytest
from sqlmodel import Session
from models import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
from crud import (
    create_task, get_task, get_tasks, update_task, delete_task, 
    bulk_update_tasks, bulk_delete_tasks, search_tasks
)

class TestCrudOperations:
    """Test class for CRUD operations."""

    def test_create_task(self, test_session: Session):
        """Test creating a task."""
        task_data = TaskCreate(
            title="Test Task",
            description="This is a test task",
            status=TaskStatus.pending,
            priority=TaskPriority.high
        )
        
        created_task = create_task(test_session, task_data)
        assert created_task.id is not None
        assert created_task.title == "Test Task"
        assert created_task.description == "This is a test task"
        assert created_task.status == TaskStatus.pending
        assert created_task.priority == TaskPriority.high
        assert created_task.created_at is not None

    def test_get_task(self, test_session: Session):
        """Test retrieving tasks."""
        # Create a task first
        task_data = TaskCreate(title="Get Task Test")
        created_task = create_task(test_session, task_data)
        
        # Get existing task
        retrieved_task = get_task(test_session, created_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == "Get Task Test"
        
        # Get non-existent task
        assert get_task(test_session, 999) is None

    def test_get_with_pagination(self, test_session: Session):
        """Test getting tasks with pagination."""
        # Empty database
        tasks, total = get_tasks(test_session)
        assert tasks == []
        assert total == 0
        
        # Create multiple tasks
        for i in range(5):
            task_data = TaskCreate(title=f"Task {i+1}")
            create_task(test_session, task_data)
        
        # Get all tasks
        tasks, total = get_tasks(test_session)
        assert len(tasks) == 5
        assert total == 5
        
        # Test pagination
        page1_tasks, page1_total = get_tasks(test_session, skip=0, limit=2)
        page2_tasks, page2_total = get_tasks(test_session, skip=2, limit=2)
        assert len(page1_tasks) == 2
        assert len(page2_tasks) == 2
        assert page1_total == 5  # Total should be same
        assert page2_total == 5
        assert page1_tasks[0].id != page2_tasks[0].id  # Different tasks

    def test_update_task(self, test_session: Session):
        """Test updating tasks."""
        # Create task
        task_data = TaskCreate(title="Original Task", description="Original")
        created_task = create_task(test_session, task_data)
        
        # Update existing task
        update_data = TaskUpdate(title="Updated Task", status=TaskStatus.completed)
        updated_task = update_task(test_session, created_task.id, update_data)
        
        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Original"  # Unchanged
        assert updated_task.status == TaskStatus.completed
        assert updated_task.updated_at is not None
        
        # Update non-existent task
        assert update_task(test_session, 999, update_data) is None

    def test_delete_task(self, test_session: Session):
        """Test deleting tasks."""
        # Create task
        task_data = TaskCreate(title="Task to Delete")
        created_task = create_task(test_session, task_data)
        
        # Delete existing task
        assert delete_task(test_session, created_task.id) is True
        assert get_task(test_session, created_task.id) is None
        
        # Delete non-existent task
        assert delete_task(test_session, 999) is False

    def test_filtering(self, test_session: Session):
        """Test filtering tasks by attributes."""
        # Create tasks with different attributes
        task1 = TaskCreate(title="Completed High", status=TaskStatus.completed, priority=TaskPriority.high, assigned_to="alice")
        task2 = TaskCreate(title="Pending Low", status=TaskStatus.pending, priority=TaskPriority.low, assigned_to="bob")
        task3 = TaskCreate(title="Completed Medium", status=TaskStatus.completed, priority=TaskPriority.medium, assigned_to="alice")
        task4 = TaskCreate(title="In Progress High", status=TaskStatus.in_progress, priority=TaskPriority.high, assigned_to="charlie")
        
        create_task(test_session, task1)
        create_task(test_session, task2)
        create_task(test_session, task3)
        create_task(test_session, task4)
        
        # Filter by status - get_tasks returns (tasks, total)
        completed_tasks, total = get_tasks(test_session, status=TaskStatus.completed)
        assert len(completed_tasks) == 2
        
        # Filter by priority
        high_priority, total = get_tasks(test_session, priority=TaskPriority.high)
        assert len(high_priority) == 2
        
        # Filter by assigned_to
        alice_tasks, total = get_tasks(test_session, assigned_to="alice")
        assert len(alice_tasks) == 2
        assert all(task.assigned_to == "alice" for task in alice_tasks)
        
        # Combine multiple filters (status + priority)
        completed_high, total = get_tasks(test_session, status=TaskStatus.completed, priority=TaskPriority.high)
        assert len(completed_high) == 1
        assert completed_high[0].title == "Completed High"

    def test_search(self, test_session: Session):
        """Test search functionality."""
        # Create tasks with searchable content
        task1 = TaskCreate(title="Python Programming", description="Learn Python basics")
        task2 = TaskCreate(title="Database Design", description="PostgreSQL and Python")
        task3 = TaskCreate(title="API Development", description="FastAPI framework")
        
        create_task(test_session, task1)
        create_task(test_session, task2)
        create_task(test_session, task3)
        
        # Search in title and description using get_tasks
        python_tasks, total = get_tasks(test_session, search="Python")
        assert len(python_tasks) == 2  # Should find tasks 1 and 2
        
        api_tasks, total = get_tasks(test_session, search="API")
        assert len(api_tasks) == 1  # Should find task 3

    def test_sorting(self, test_session: Session):
        """Test sorting functionality."""
        from datetime import datetime, timedelta
        
        # Create tasks with different attributes for sorting
        task1 = TaskCreate(title="Alpha Task", priority=TaskPriority.low, status=TaskStatus.pending)
        task2 = TaskCreate(title="Beta Task", priority=TaskPriority.high, status=TaskStatus.completed)
        task3 = TaskCreate(title="Gamma Task", priority=TaskPriority.medium, status=TaskStatus.in_progress)
        
        created_task1 = create_task(test_session, task1)
        created_task2 = create_task(test_session, task2)
        created_task3 = create_task(test_session, task3)
        
        # Test sorting by title ascending
        tasks_title_asc, total = get_tasks(test_session, sort_by="title", sort_order="asc")
        assert len(tasks_title_asc) == 3
        assert tasks_title_asc[0].title == "Alpha Task"
        assert tasks_title_asc[1].title == "Beta Task"
        assert tasks_title_asc[2].title == "Gamma Task"
        
        # Test sorting by title descending
        tasks_title_desc, total = get_tasks(test_session, sort_by="title", sort_order="desc")
        assert len(tasks_title_desc) == 3
        assert tasks_title_desc[0].title == "Gamma Task"
        assert tasks_title_desc[1].title == "Beta Task"
        assert tasks_title_desc[2].title == "Alpha Task"

    def test_bulk_update(self, test_session: Session):
        """Test bulk update operations."""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            task_data = TaskCreate(title=f"Bulk Update Task {i+1}", status=TaskStatus.pending)
            created_task = create_task(test_session, task_data)
            task_ids.append(created_task.id)
        
        # Bulk update
        update_data = TaskUpdate(status=TaskStatus.completed, priority=TaskPriority.high)
        updated_tasks = bulk_update_tasks(test_session, task_ids, update_data)
        assert len(updated_tasks) == 3
        
        # Verify updates
        for task_id in task_ids:
            task = get_task(test_session, task_id)
            assert task.status == TaskStatus.completed
            assert task.priority == TaskPriority.high

    def test_bulk_delete(self, test_session: Session):
        """Test bulk delete operations."""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            task_data = TaskCreate(title=f"Bulk Delete Task {i+1}")
            created_task = create_task(test_session, task_data)
            task_ids.append(created_task.id)
        
        # Verify tasks exist
        for task_id in task_ids:
            assert get_task(test_session, task_id) is not None
        
        # Bulk delete
        deleted_count = bulk_delete_tasks(test_session, task_ids)
        assert deleted_count == 3
        
        # Verify deletions
        for task_id in task_ids:
            assert get_task(test_session, task_id) is None
