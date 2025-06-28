from datetime import datetime
from typing import List, Optional, Tuple
from sqlmodel import Session, delete, select, update
from models import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority, create_task_filter


def create_task(session: Session, task: TaskCreate) -> Task:
    """Create a new task"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def get_task(session: Session, task_id: int) -> Optional[Task]:
    """Get a task by ID"""
    return session.get(Task, task_id)


def get_tasks(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assigned_to: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    due_before: Optional[datetime] = None,
    search: Optional[str] = None,
    has_due_date: Optional[bool] = None,
    is_overdue: Optional[bool] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc"
) -> Tuple[List[Task], int]:
    """
    Get tasks with advanced filtering using Builder pattern.
    Returns tuple of (tasks, total_count).
    """
    filter_builder = (create_task_filter()
                     .session(session)
                     .by_status(status)
                     .by_priority(priority)
                     .by_assigned_to(assigned_to)
                     .created_between(created_after, created_before)
                     .due_between(due_after, due_before)
                     .search_text(search)
                     .has_due_date(has_due_date)
                     .is_overdue(is_overdue)
                     .order_by(sort_by, sort_order)
                     .with_pagination(skip, limit))
    
    return filter_builder.execute()


def get_tasks_by_status(session: Session, status: TaskStatus) -> List[Task]:
    """Get tasks by status"""
    statement = select(Task).where(Task.status == status)
    result = session.exec(statement)
    return result.all()


def get_tasks_by_priority(session: Session, priority: TaskPriority) -> List[Task]:
    """Get tasks by priority"""
    statement = select(Task).where(Task.priority == priority)
    result = session.exec(statement)
    return result.all()


def update_task(session: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    """Update a task"""
    db_task = session.get(Task, task_id)
    if not db_task:
        return None
    
    task_data = task_update.model_dump(exclude_unset=True)
    if task_data:
        task_data['updated_at'] = datetime.now()
        for key, value in task_data.items():
            setattr(db_task, key, value)
        
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
    
    return db_task


def delete_task(session: Session, task_id: int) -> bool:
    """Delete a task"""
    db_task = session.get(Task, task_id)
    if not db_task:
        return False
    
    session.delete(db_task)
    session.commit()
    return True


def get_tasks_count(session: Session) -> int:
    """Get total count of tasks"""
    statement = select(Task)
    result = session.exec(statement)
    return len(result.all())


def bulk_update_tasks(
    session: Session, 
    task_ids: List[int], 
    task_update: TaskUpdate
) -> List[Task]:
    """Bulk update multiple tasks"""
    updated_tasks = []
    task_data = task_update.model_dump(exclude_unset=True)
    
    if task_data:
        task_data['updated_at'] = datetime.now()
        
        existing_tasks = session.exec(select(Task).where(Task.id.in_(task_ids))).all()

        if len(existing_tasks) != len(task_ids):
            existing_ids = [task.id for task in existing_tasks]
            missing_ids = list(set(task_ids) - set(existing_ids))
            raise ValueError(f"Tasks not found: {missing_ids}")

        stmt = (
                update(Task)
                .where(Task.id.in_(task_ids))
                .values(**task_data)
            )
        session.exec(stmt)
        session.commit()
        
        updated_tasks = session.exec(
        select(Task).where(Task.id.in_(task_ids))
    ).all()
        
    
    return updated_tasks


def bulk_delete_tasks(session: Session, task_ids: List[int]) -> int:
    existing_tasks = session.exec(select(Task).where(Task.id.in_(task_ids))).all()

    if len(existing_tasks) != len(task_ids):
        existing_ids = [task.id for task in existing_tasks]
        missing_ids = list(set(task_ids) - set(existing_ids))
        raise ValueError(f"Tasks not found: {missing_ids}")
    
    stmt = (
        delete(Task)
        .where(Task.id.in_(task_ids))
    )
    
    result = session.exec(stmt)
    affected_count = result.rowcount
    session.commit()
    return affected_count


def search_tasks(session: Session, search_term: str) -> List[Task]:
    """Search tasks by title or description"""
    search_pattern = f"%{search_term}%"
    statement = select(Task).where(
        (Task.title.ilike(search_pattern)) | 
        (Task.description.ilike(search_pattern))
    )
    result = session.exec(statement)
    return result.all()
