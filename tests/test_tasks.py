"""
Unit tests for Task API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestTaskEndpoints:
    """Test class for Task API endpoints"""

    def test_create_task_valid_data(self, client: TestClient, sample_task_data):
        """Test creating a task with valid data."""
        response = client.post("/tasks", json=sample_task_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["status"] == sample_task_data["status"]
        assert "created_at" in data

    def test_create_task_minimal_data(self, client: TestClient):
        """Test creating a task with minimal required data."""
        task_data = {"title": "Minimal Task"}
        response = client.post("/tasks", json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["status"] == "pending"

    def test_create_task_validation_errors(self, client: TestClient):
        """Test task creation validation errors."""
        # Empty title
        response = client.post("/tasks", json={"title": ""})
        assert response.status_code == 422
        
        # Too long title
        response = client.post("/tasks", json={"title": "x" * 201})
        assert response.status_code == 422

    def test_get_task_existing(self, client: TestClient, created_task):
        """Test retrieving an existing task."""
        task_id = created_task["id"]
        response = client.get(f"/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == task_id
        assert data["title"] == created_task["title"]

    def test_get_task_nonexistent(self, client: TestClient):
        """Test retrieving a non-existent task."""
        response = client.get("/tasks/999")
        assert response.status_code == 404

    def test_get_tasks_empty(self, client: TestClient):
        """Test getting tasks when database is empty."""
        response = client.get("/tasks")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tasks"] == []
        assert data["total"] == 0

    def test_get_tasks_with_data(self, client: TestClient, created_multiple_tasks):
        """Test getting tasks when data exists."""
        response = client.get("/tasks")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tasks"]) == 3
        assert data["total"] == 3

    def test_get_tasks_pagination(self, client: TestClient, created_multiple_tasks):
        """Test task list pagination."""
        response = client.get("/tasks?page=1&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tasks"]) == 2
        assert data["total"] == 3
        assert data["has_next"] is True
        assert data["has_previous"] is False

    def test_get_tasks_filtering(self, client: TestClient):
        """Test filtering tasks."""
        # Create tasks with different statuses
        client.post("/tasks", json={"title": "Completed Task", "status": "completed"})
        client.post("/tasks", json={"title": "Pending Task", "status": "pending"})
        
        # Filter by status
        response = client.get("/tasks?status=completed")
        data = response.json()
        
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["status"] == "completed"

    def test_get_tasks_search(self, client: TestClient):
        """Test searching tasks."""
        # Create tasks with searchable content
        client.post("/tasks", json={"title": "Python Programming"})
        client.post("/tasks", json={"title": "Java Development"})
        
        response = client.get("/tasks?search=Python")
        data = response.json()
        
        assert len(data["tasks"]) == 1
        assert "Python" in data["tasks"][0]["title"]

    def test_update_task_existing(self, client: TestClient, created_task):
        """Test updating an existing task."""
        task_id = created_task["id"]
        update_data = {"title": "Updated Task", "status": "completed"}
        
        response = client.put(f"/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "Updated Task"
        assert data["status"] == "completed"

    def test_update_task_nonexistent(self, client: TestClient):
        """Test updating a non-existent task."""
        response = client.put("/tasks/999", json={"title": "Updated"})
        assert response.status_code in [400, 404]

    def test_delete_task_existing(self, client: TestClient, created_task):
        """Test deleting an existing task."""
        task_id = created_task["id"]
        response = client.delete(f"/tasks/{task_id}")
        
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 404

    def test_delete_task_nonexistent(self, client: TestClient):
        """Test deleting a non-existent task."""
        response = client.delete("/tasks/999")
        assert response.status_code == 404

    def test_get_tasks_by_status(self, client: TestClient):
        """Test getting tasks by status endpoint."""
        # Create a completed task
        client.post("/tasks", json={"title": "Done Task", "status": "completed"})
        
        response = client.get("/tasks/status/completed")
        assert response.status_code == 200
        
        data = response.json()
        assert all(task["status"] == "completed" for task in data)

    def test_get_tasks_by_priority(self, client: TestClient):
        """Test getting tasks by priority endpoint."""
        # Create a high priority task
        client.post("/tasks", json={"title": "Urgent Task", "priority": "high"})
        
        response = client.get("/tasks/priority/high")
        assert response.status_code == 200
        
        data = response.json()
        assert all(task["priority"] == "high" for task in data)

    def test_bulk_update_tasks(self, client: TestClient, created_multiple_tasks):
        """Test bulk updating tasks."""
        task_ids = [task["id"] for task in created_multiple_tasks]
        
        bulk_data = {
            "task_ids": task_ids,
            "update_data": {"status": "completed"}
        }
        response = client.post("/tasks/bulk/update", json=bulk_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["affected_count"] == 3

    def test_bulk_delete_tasks(self, client: TestClient, created_multiple_tasks):
        """Test bulk deleting tasks."""
        task_ids = [task["id"] for task in created_multiple_tasks]
        
        bulk_data = {"task_ids": task_ids}
        response = client.post("/tasks/bulk/delete", json=bulk_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["affected_count"] == 3