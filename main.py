from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database import create_db_and_tables
from routers import tasks

# Environment variables from .env file (no defaults - .env is source of truth)
API_TITLE = os.environ["API_TITLE"]
API_DESCRIPTION = os.environ["API_DESCRIPTION"]
API_VERSION = os.environ["API_VERSION"]
HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")
ENVIRONMENT = os.environ["ENVIRONMENT"]
DATABASE_URL = os.environ["DATABASE_URL"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup"""
    create_db_and_tables()
    yield


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

# Include the tasks router
app.include_router(tasks.router)


@app.get("/")
async def root():
    """Root endpoint - Return API information and available endpoints"""
    
    # Core endpoints (non-router endpoints)
    core_endpoints = {
        "GET /": "Root endpoint - API information and available endpoints",
        "GET /docs": "Interactive API documentation (Swagger UI)",
        "GET /redoc": "Alternative API documentation (ReDoc)",
        "GET /openapi.json": "OpenAPI schema in JSON format",
        "GET /health": "Health check endpoint"
    }
    
    # Router endpoints grouped by router
    router_endpoints = {}
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            # Skip internal FastAPI routes and core endpoints
            if route.path.startswith(('/docs', '/openapi', '/redoc')) or route.path in ['/', '/health']:
                continue
            
            # Extract router name from path (first segment after /)
            path_parts = route.path.strip('/').split('/')
            if path_parts and path_parts[0]:
                router_name = path_parts[0]
                
                # Initialize router group if not exists
                if router_name not in router_endpoints:
                    router_endpoints[router_name] = {}
                
                # Add endpoint information for each HTTP method
                for method in route.methods:
                    if method != 'HEAD':  # Skip HEAD method
                        # Get endpoint description from docstring
                        endpoint_func = getattr(route, 'endpoint', None)
                        description = "No description available"
                        if endpoint_func and hasattr(endpoint_func, '__doc__') and endpoint_func.__doc__:
                            # Extract first line of docstring for concise description
                            doc_lines = endpoint_func.__doc__.strip().split('\n')
                            description = doc_lines[0].strip() if doc_lines else "No description available"
                        
                        # Format: "GET /tasks/{id} -- Get a specific task by ID"
                        endpoint_key = f"{method} {route.path}"
                        router_endpoints[router_name][endpoint_key] = description
    
    return {
        "endpoints": {
            **{path: desc for path, desc in core_endpoints.items()},
            "routers": router_endpoints
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": API_TITLE,
        "version": API_VERSION,
        "environment": ENVIRONMENT,
        "database_url": DATABASE_URL.split("///")[-1] if "sqlite" in DATABASE_URL else "external_db"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=HOST, 
        port=PORT, 
        reload=DEBUG
    )
