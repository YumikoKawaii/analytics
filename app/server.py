from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import health, files
from app.exceptions import ServiceException

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Custom exception handler for ServiceException
@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    """
    Handle ServiceException and return consistent error response.
    Excludes null fields from the response.
    """
    response_data = {
        "code": exc.code,
        "message": exc.message,
    }

    # Only include data if it's not None
    if exc.data is not None:
        response_data["data"] = exc.data

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(files.router)

@app.get("/")
async def root():
    """
    Root endpoint returning basic API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }
