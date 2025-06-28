from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime

from database import get_session
from models import (
    Task, TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority,
    BulkUpdateRequest, BulkDeleteRequest, BulkOperationResponse, TaskListResponse
)
import crud

# Create router for task-related endpoints
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)


# Task CRUD endpoints
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    """Create a new task"""
    try:
        db_task = crud.create_task(session=session, task=task)
        return db_task
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating task: {str(e)}")


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    # Basic filters
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assignee (partial match)"),
    # Date filters
    created_after: Optional[datetime] = Query(None, description="Filter tasks created after this date"),
    created_before: Optional[datetime] = Query(None, description="Filter tasks created before this date"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks with due date after this date"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks with due date before this date"),
    # Search and special filters
    search: Optional[str] = Query(None, description="Search in title and description"),
    has_due_date: Optional[bool] = Query(None, description="Filter tasks with/without due dates"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue tasks"),
    # Sorting
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    session: Session = Depends(get_session)
):
    """
    List all tasks with advanced filtering using Builder pattern.
    
    ## Advanced Filtering Features:
    - **Basic Filters**: status, priority, assigned_to
    - **Date Range Filters**: created_after/before, due_after/before  
    - **Search**: Text search in title and description
    - **Special Filters**: has_due_date, is_overdue
    - **Sorting**: Sort by any field with asc/desc order
    - **Pagination**: Page-based pagination with metadata
    
    ## Examples:
    - Get high priority pending tasks: `?status=pending&priority=high`
    - Get overdue tasks: `?is_overdue=true&sort_by=due_date&sort_order=asc`
    - Search recent tasks: `?search=urgent&created_after=2024-01-01`
    - Get tasks assigned to user: `?assigned_to=john&page=1&page_size=20`
    """
    try:
        # Calculate skip offset
        skip = (page - 1) * page_size
        
        # Use the advanced filtering function from crud
        tasks, total = crud.get_tasks(
            session=session,
            skip=skip,
            limit=page_size,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            created_after=created_after,
            created_before=created_before,
            due_after=due_after,
            due_before=due_before,
            search=search,
            has_due_date=has_due_date,
            is_overdue=is_overdue,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        # Collect applied filters for response
        filters_applied = {
            k: v for k, v in {
                "status": status,
                "priority": priority,
                "assigned_to": assigned_to,
                "created_after": created_after,
                "created_before": created_before,
                "due_after": due_after,
                "due_before": due_before,
                "search": search,
                "has_due_date": has_due_date,
                "is_overdue": is_overdue,
                "sort_by": sort_by,
                "sort_order": sort_order
            }.items() if v is not None
        }
        
        return TaskListResponse(
            tasks=tasks,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
            filters_applied=filters_applied
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving tasks: {str(e)}")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, session: Session = Depends(get_session)):
    """Retrieve a specific task"""
    db_task = crud.get_task(session=session, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing task"""
    try:
        db_task = crud.update_task(session=session, task_id=task_id, task_update=task_update)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating task: {str(e)}")


@router.delete("/{task_id}")
async def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Delete a task"""
    success = crud.delete_task(session=session, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# Filtering endpoints
@router.get("/status/{status}", response_model=List[TaskResponse])
async def get_tasks_by_status(status: TaskStatus, session: Session = Depends(get_session)):
    """Get tasks by status"""
    try:
        tasks = crud.get_tasks_by_status(session=session, status=status)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving tasks: {str(e)}")


@router.get("/priority/{priority}", response_model=List[TaskResponse])
async def get_tasks_by_priority(priority: TaskPriority, session: Session = Depends(get_session)):
    """Get tasks by priority"""
    try:
        tasks = crud.get_tasks_by_priority(session=session, priority=priority)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving tasks: {str(e)}")


# Bulk operations
@router.post("/bulk/update", response_model=BulkOperationResponse)
async def bulk_update_tasks(
    bulk_request: BulkUpdateRequest,
    session: Session = Depends(get_session)
):
    """Bulk update multiple tasks"""
    try:
        updated_tasks = crud.bulk_update_tasks(
            session=session,
            task_ids=bulk_request.task_ids,
            task_update=bulk_request.update_data
        )
        return BulkOperationResponse(
            success=True,
            message=f"Successfully updated {len(updated_tasks)} tasks",
            affected_count=len(updated_tasks),
            tasks=updated_tasks
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error bulk updating tasks: {str(e)}")


@router.post("/bulk/delete", response_model=BulkOperationResponse)
async def bulk_delete_tasks(
    bulk_request: BulkDeleteRequest,
    session: Session = Depends(get_session)
):
    """Bulk delete multiple tasks"""
    try:
        deleted_count = crud.bulk_delete_tasks(
            session=session,
            task_ids=bulk_request.task_ids
        )
        return BulkOperationResponse(
            success=True,
            message=f"Successfully deleted {deleted_count} tasks",
            affected_count=deleted_count
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error bulk deleting tasks: {str(e)}")
