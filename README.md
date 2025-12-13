# Analytics API

A simple FastAPI application with health and readiness check endpoints.

## Project Structure

```
analytics/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Application settings
│   └── routers/
│       ├── __init__.py
│       └── health.py        # Health and readiness endpoints
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── README.md
```

## Features

- FastAPI framework
- Health check endpoint
- Readiness check endpoint
- CORS middleware
- Environment-based configuration
- Auto-reload in debug mode

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Using the main.py script
```bash
python main.py
```

### Method 2: Using uvicorn directly
```bash
uvicorn app.main:app --reload
```

The application will start on `http://localhost:8000`

## API Endpoints

### Root Endpoint
- **GET** `/`
  - Returns basic API information

### Health Check
- **GET** `/health`
  - Returns the health status of the application
  - Response:
    ```json
    {
      "status": "healthy",
      "timestamp": "2025-12-13T12:00:00.000000",
      "service": "analytics-api"
    }
    ```

### Readiness Check
- **GET** `/readiness`
  - Returns whether the application is ready to accept traffic
  - Response:
    ```json
    {
      "status": "ready",
      "timestamp": "2025-12-13T12:00:00.000000",
      "checks": {
        "database": "ready",
        "cache": "ready",
        "external_services": "ready"
      }
    }
    ```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

Configuration is managed through the `app/config.py` file. You can override settings using environment variables or a `.env` file:

```env
APP_NAME=Analytics API
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Development

To run the application in development mode with auto-reload:

```bash
python main.py
```

or

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
