from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    Returns basic health status of the application.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "analytics-api"
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint.
    Returns whether the application is ready to accept traffic.
    This can include checks for database connections, external services, etc.
    """
    # In a real application, you would check:
    # - Database connectivity
    # - External service dependencies
    # - Cache availability
    # - Message queue connections

    checks = {
        "database": "ready",
        "cache": "ready",
        "external_services": "ready"
    }

    all_ready = all(check == "ready" for check in checks.values())

    return {
        "status": "ready" if all_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
