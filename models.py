from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, select, and_, or_, func
from pydantic import field_validator


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


# Database model
class TaskBase(SQLModel):
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = Field(default=None, max_length=100)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v is not None:
            # Make both datetimes timezone-naive for comparison
            now = datetime.now()
            if v.tzinfo is not None:
                v = v.replace(tzinfo=None)
            if v <= now:
                raise ValueError('Due date must be in the future')
        return v


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


# Request/Response models
class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = Field(default=None, max_length=100)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else v

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v is not None:
            now = datetime.now()
            if v.tzinfo is not None:
                v = v.replace(tzinfo=None)
            if v <= now:
                raise ValueError('Due date must be in the future')
        return v


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Bulk operation models
class BulkUpdateRequest(SQLModel):
    task_ids: List[int]
    update_data: TaskUpdate


class BulkDeleteRequest(SQLModel):
    task_ids: List[int]


class BulkOperationResponse(SQLModel):
    success: bool
    message: str
    affected_count: int
    tasks: Optional[List[TaskResponse]] = None


class TaskListResponse(SQLModel):
    """Response model for task list with metadata."""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    filters_applied: dict = {}


# Advanced filtering using Builder design pattern
class TaskFilterBuilder:
    """Builder class for constructing complex task filters."""
    
    def __init__(self):
        self.conditions = []
        self._session = None
        self._base_query = select(Task)
        
    def session(self, session):
        """Set the database session."""
        self._session = session
        return self
    
    def by_status(self, status: Optional[TaskStatus]):
        """Filter by task status."""
        if status:
            self.conditions.append(Task.status == status)
        return self
    
    def by_priority(self, priority: Optional[TaskPriority]):
        """Filter by task priority."""
        if priority:
            self.conditions.append(Task.priority == priority)
        return self
    
    def by_assigned_to(self, assigned_to: Optional[str]):
        """Filter by assignee name (partial match)."""
        if assigned_to:
            self.conditions.append(Task.assigned_to.ilike(f"%{assigned_to}%"))
        return self
    
    def created_between(self, start_date: Optional[datetime], end_date: Optional[datetime]):
        """Filter by creation date range."""
        if start_date:
            self.conditions.append(Task.created_at >= start_date)
        if end_date:
            self.conditions.append(Task.created_at <= end_date)
        return self
    
    def due_between(self, start_date: Optional[datetime], end_date: Optional[datetime]):
        """Filter by due date range."""
        if start_date:
            self.conditions.append(Task.due_date >= start_date)
        if end_date:
            self.conditions.append(Task.due_date <= end_date)
        return self
    
    def search_text(self, search_term: Optional[str]):
        """Search in title and description."""
        if search_term:
            search_pattern = f"%{search_term}%"
            self.conditions.append(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )
        return self
    
    def has_due_date(self, has_due: Optional[bool]):
        """Filter tasks that have or don't have due dates."""
        if has_due is not None:
            if has_due:
                self.conditions.append(Task.due_date.is_not(None))
            else:
                self.conditions.append(Task.due_date.is_(None))
        return self
    
    def is_overdue(self, overdue: Optional[bool]):
        """Filter overdue tasks."""
        if overdue is not None:
            now = datetime.now()
            if overdue:
                self.conditions.append(
                    and_(
                        Task.due_date.is_not(None),
                        Task.due_date < now,
                        Task.status != TaskStatus.completed
                    )
                )
            else:
                self.conditions.append(
                    or_(
                        Task.due_date.is_(None),
                        Task.due_date >= now,
                        Task.status == TaskStatus.completed
                    )
                )
        return self
    
    def with_pagination(self, skip: int = 0, limit: int = 100):
        """Add pagination to the query."""
        self._skip = skip
        self._limit = limit
        return self
    
    def order_by(self, field: str, direction: str = "asc"):
        """Add ordering to the query."""
        if hasattr(Task, field):
            column = getattr(Task, field)
            if direction.lower() == "desc":
                self._base_query = self._base_query.order_by(column.desc())
            else:
                self._base_query = self._base_query.order_by(column.asc())
        return self
    
    def build_query(self):
        """Build the final query with all conditions."""
        query = self._base_query
        
        if self.conditions:
            query = query.where(and_(*self.conditions))
        
        return query
    
    def build_count_query(self):
        """Build a count query with the same conditions."""
        query = select(func.count(Task.id))
        
        if self.conditions:
            query = query.where(and_(*self.conditions))
        
        return query
    
    def execute(self):
        """Execute the query and return results with pagination."""
        if not self._session:
            raise ValueError("Session must be set before executing query")
        
        # Get total count
        count_query = self.build_count_query()
        total = self._session.exec(count_query).one()
        
        # Get paginated results
        query = self.build_query()
        
        # Apply pagination
        if hasattr(self, '_skip') and hasattr(self, '_limit'):
            query = query.offset(self._skip).limit(self._limit)
        
        results = self._session.exec(query).all()
        
        return results, total
    
    def execute_simple(self):
        """Execute the query and return just the results (no count)."""
        if not self._session:
            raise ValueError("Session must be set before executing query")
        
        query = self.build_query()
        
        # Apply pagination
        if hasattr(self, '_skip') and hasattr(self, '_limit'):
            query = query.offset(self._skip).limit(self._limit)
        
        return self._session.exec(query).all()


def create_task_filter():
    """Factory function to create a new TaskFilterBuilder instance."""
    return TaskFilterBuilder()
