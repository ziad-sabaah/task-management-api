# Task Management API

A comprehensive task management API built with FastAPI, Pydantic, and SQLModel. This API provides a complete task management solution with advanced features, testing, and containerization support.

## 🏆 Project Status - COMPLETED

This project fully implements all requirements from the task specification plus some bonus features:

### ✅ **Core Requirements**
- **Full CRUD Operations** - Create, Read, Update, Delete tasks with proper validation
- **RESTful API Design** - Proper HTTP methods, status codes, and endpoint naming
- **Database Integration** - SQLModel/SQLAlchemy with SQLite, automatic table creation
- **Data Validation** - Comprehensive Pydantic models with custom validators
- **Error Handling** - Proper error responses (201, 200, 404, 422, 400)
- **API Documentation** - Automatic OpenAPI/Swagger documentation
- **Environment Configuration** - Support for different environments via .env

### ✅ **Bonus Features Implemented**
- **Advanced Filtering** - Multiple simultaneous filters (status, priority, assigned_to, dates)
- **Sorting** - Sort tasks by any field (title, created_at, etc.) with asc/desc order
- **Search** - Full-text search in title and description
- **Bulk Operations** - Efficient bulk update and delete operations
- **Pagination** - Page-based pagination with metadata (has_next, has_previous)
- **Unit Tests** - Comprehensive test coverage (85%+) with pytest
- **Docker Support** - Containerized application with Dockerfile
- **Clean Architecture** - Modular design with routers, CRUD separation
- **Builder Pattern** - Advanced filtering using TaskFilterBuilder pattern

### 🧪 **Testing & Quality Assurance**
- **Comprehensive Test Suite** - Unit tests for all components (CRUD, models, endpoints)
- **Test Coverage** - 85%+ code coverage with pytest and coverage
- **Integration Tests** - End-to-end API testing
- **Test Fixtures** - Reusable test data and database setup


## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQL databases in Python, designed for simplicity and type safety
- **Pydantic** - Data validation using Python type annotations
- **SQLite** - Lightweight database for development and testing
- **Uvicorn** - Lightning-fast ASGI server
- **Pytest** - Testing framework with fixtures and coverage
- **Docker** - Containerization support

## Project Structure

```
BuGuard_Task/
├── main.py               # FastAPI application entry point
├── models.py             # Pydantic/SQLModel data models & TaskFilterBuilder
├── database.py           # Database configuration and session management
├── crud.py               # Database CRUD operations with advanced filtering
├── requirements.txt      # Python dependencies
├── README.md             # This documentation
├── Dockerfile            # Docker container configuration
├── .dockerignore         # Docker ignore patterns
├── .gitignore            # Git ignore patterns
├── .env.example          # Example Environment variables
├── pyproject.toml        # Project configuration and test settings
├── conftest.py           # Pytest configuration and fixtures
├── routers/              # API routers for organized endpoint management
│   ├── __init__.py       # Router package initialization
│   └── tasks.py          # All task-related API endpoints
├── tests/                # Comprehensive test suite
│   ├── __init__.py       # Test package initialization
│   ├── test_main.py      # Main application tests
│   ├── test_models.py    # Model validation tests
│   ├── test_crud.py      # CRUD function tests
│   └── test_tasks.py     # API endpoint tests
└── tasks.db              # SQLite database (created automatically)
```

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ziad-sabaah/task-management-api
   cd task-management-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit the .env file with your configuration
   # On Windows: notepad .env
   # On macOS/Linux: nano .env or vim .env
   ```
   
   **Important:** Update the `.env` file with appropriate values for your environment:
   - Set `DEBUG=false` for production
   - Update `DATABASE_URL` for production databases (PostgreSQL/MySQL)
   - Modify `HOST` and `PORT` as needed
   - Set `ENVIRONMENT` to match your deployment stage

5. **Run the application**
   ```bash
   python main.py
   ```

### Docker Setup

1. **Build Docker image**
   ```bash
   docker build -t task-management-api .
   ```

2. **Run Docker container with environment file**
   ```bash
   # Create .env file first (copy from .env.example and edit)
   cp .env.example .env
   # Edit .env file as needed
   
   # Run container with environment file
   docker run -p 8000:8000 --env-file .env task-management-api
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation (Swagger UI):** http://localhost:8000/docs
- **Alternative Documentation (ReDoc):** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## API Endpoints

### Core Endpoints

- `GET /` - API information and dynamically generated available endpoints
- `GET /health` - API health status


### Task Management (All under `/tasks`)

#### Basic CRUD Operations
- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks with advanced filtering, search, sorting, and pagination
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update an existing task
- `DELETE /tasks/{task_id}` - Delete a task

#### Advanced Filtering & Search
- `GET /tasks?status=pending` - Filter by status
- `GET /tasks?priority=high` - Filter by priority  
- `GET /tasks?assigned_to=john` - Filter by assignee
- `GET /tasks?search=python` - Search in title/description
- `GET /tasks?created_after=2024-01-01` - Date range filtering
- `GET /tasks?has_due_date=true` - Filter tasks with/without due dates
- `GET /tasks?is_overdue=true` - Find overdue tasks

#### Sorting & Pagination
- `GET /tasks?sort_by=title&sort_order=asc` - Sort by any field
- `GET /tasks?page=1&page_size=20` - Page-based pagination

#### Specialized Endpoints
- `GET /tasks/status/{status}` - Get tasks by specific status
- `GET /tasks/priority/{priority}` - Get tasks by specific priority

#### Bulk Operations
- `POST /tasks/bulk/update` - Update multiple tasks at once
- `POST /tasks/bulk/delete` - Delete multiple tasks at once

## Data Models

### Task Model
```python
{
    "id": 1,                           # Auto-generated primary key
    "title": "Complete API project",   # Required, max 200 chars
    "description": "Build FastAPI...", # Optional, max 1000 chars
    "status": "pending",               # Enum: pending, in_progress, completed, cancelled
    "priority": "high",                # Enum: low, medium, high, urgent
    "created_at": "2024-01-01T10:00:00Z", # Auto-generated timestamp
    "updated_at": "2024-01-01T11:00:00Z", # Auto-updated on changes
    "due_date": "2024-01-15T23:59:59Z",   # Optional, must be in future
    "assigned_to": "john.doe"             # Optional, max 100 chars
}
```

### Validation Rules
- **Title**: Cannot be empty or whitespace only, automatically trimmed
- **Due Date**: Must be in the future if provided
- **Status/Priority**: Must be valid enum values
- **Field Lengths**: Enforced maximum lengths for all string fields

## Data Models

### Task Model

| Field       | Type     | Constraints                  | Description            |
|-------------|----------|------------------------------|------------------------|
| id          | Integer  | Primary Key, Auto-increment  | Unique task identifier |
| title       | String   | Required, Max 200 chars     | Task title             |
| description | String   | Optional, Max 1000 chars    | Task description       |
| status      | Enum     | Required, Default: "pending" | Task status            |
| priority    | Enum     | Required, Default: "medium"  | Task priority          |
| created_at  | DateTime | Auto-generated              | Creation timestamp     |
| updated_at  | DateTime | Optional                    | Last update timestamp  |
| due_date    | DateTime | Optional                    | Task deadline          |
| assigned_to | String   | Optional, Max 100 chars     | Assignee name          |

### Enums

**TaskStatus:**
- `pending`
- `in_progress`
- `completed`
- `cancelled`

**TaskPriority:**
- `low`
- `medium`
- `high`
- `urgent`

## Example API Calls

### Create a Task

```bash
curl -X POST "http://localhost:8000/tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Complete FastAPI Assessment",
       "description": "Build a comprehensive task management API",
       "priority": "high",
       "status": "in_progress",
       "assigned_to": "John Doe",
       "due_date": "2025-06-29T23:59:59"
     }'
```

### Get All Tasks with Filtering

```bash
# Get all tasks
curl -X GET "http://localhost:8000/tasks"

# Get tasks with filtering and pagination
curl -X GET "http://localhost:8000/tasks?status=pending&priority=high&skip=0&limit=10"

# Search tasks
curl -X GET "http://localhost:8000/tasks/search?q=FastAPI"
```

### Get a Specific Task

```bash
curl -X GET "http://localhost:8000/tasks/1"
```

### Update a Task

```bash
curl -X PUT "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "completed",
       "description": "Task completed successfully"
     }'
```

### Delete a Task

```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

### Bulk Operations

#### Bulk Update Tasks
```bash
curl -X POST "http://localhost:8000/tasks/bulk/update" \
     -H "Content-Type: application/json" \
     -d '{
       "task_ids": [1, 2, 3],
       "update_data": {
         "status": "completed",
         "priority": "low"
       }
     }'
```

#### Bulk Delete Tasks
```bash
curl -X POST "http://localhost:8000/tasks/bulk/delete" \
     -H "Content-Type: application/json" \
     -d '{
       "task_ids": [1, 2, 3]
     }'
```


## Validation Rules

The API implements comprehensive validation:

1. **Title Validation:**
   - Cannot be empty or whitespace only
   - Automatically trimmed of leading/trailing spaces
   - Maximum 200 characters

2. **Due Date Validation:**
   - Must be in the future (if provided)
   - Handles both timezone-aware and timezone-naive datetimes
   - Uses ISO 8601 format

3. **Field Length Validation:**
   - Description: Max 1000 characters
   - Assigned to: Max 100 characters

4. **HTTP Status Codes:**
   - `201` - Created (successful task creation)
   - `200` - OK (successful retrieval/update)
   - `404` - Not Found (task doesn't exist)
   - `422` - Unprocessable Entity (validation errors)
   - `400` - Bad Request (other client errors)

5. **Bulk Operation Validation:**
   - Validates all task IDs exist before performing operations
   - Returns detailed error messages for missing tasks
   - Ensures data integrity with proper transaction handling

### Key Design Decisions

1. **Separation of Validation**: Used validation mixins to separate validation logic from database models
2. **Bulk Operations**: Implemented true SQL bulk operations instead of loops for better performance
3. **Router Architecture**: Organized endpoints by feature for scalability and maintainability
4. **Error Handling**: Centralized error handling with meaningful HTTP status codes
5. **Type Safety**: Comprehensive type hints throughout the codebase
6. **Filteration**: Implemented using builder pattern 



## Unit Testing

This project includes comprehensive unit tests using pytest. The tests cover all major functionality including models, CRUD operations, API endpoints, and database operations.

### Test Structure

```
./
├── conftest.py          # Pytest configuration and fixtures
└── tests/
   ├── __init__.py          # Test package initialization
   ├── test_main.py         # Tests for main application endpoints
   ├── test_models.py       # Tests for Pydantic model validation
   ├── test_crud.py         # Tests for database CRUD operations
   └── test_tasks.py        # Tests for task API endpoints

```

### Running Tests

#### Basic Test Run
```bash
# Run all unit tests
pytest tests/ -m unit -v

# Run all tests (if you don't want to filter by markers)
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test method
pytest tests/test_models.py::TestTaskModel::test_task_create_valid_data -v
```

#### Test Coverage (Optional)
If you have `pytest-cov` installed:
```bash
# Run tests with coverage report
pytest tests/ -m unit --cov=. --cov-report=term-missing --cov-report=html:htmlcov

# View coverage report in browser
# Open htmlcov/index.html in your browser
```

## API Usage Examples

### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Complete FastAPI Assessment",
       "description": "Build a comprehensive task management API",
       "priority": "high",
       "due_date": "2024-12-31T23:59:59"
     }'
```

### Get All Tasks with Filtering
```bash
# Get high priority pending tasks
curl "http://localhost:8000/tasks?status=pending&priority=high"

# Search tasks with pagination
curl "http://localhost:8000/tasks?search=python&page=1&page_size=10"

# Get overdue tasks sorted by due date
curl "http://localhost:8000/tasks?is_overdue=true&sort_by=due_date&sort_order=asc"
```

### Update a Task
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{"status": "completed", "priority": "medium"}'
```
