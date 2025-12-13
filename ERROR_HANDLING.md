# Error Handling Documentation

This document explains the custom error handling implementation in the Analytics API.

## Overview

The API uses a custom exception handler to provide consistent error responses that match the standard `Response` model structure across both success and error cases.

## Components

### 1. ServiceException (`app/exceptions.py`)

Custom exception class for service-layer errors:

```python
class ServiceException(Exception):
    def __init__(
        self,
        code: int,
        message: str,
        data: Optional[Any] = None,
        status_code: Optional[int] = None
    ):
        self.code = code
        self.message = message
        self.data = data
        self.status_code = status_code or code
```

### 2. Exception Handler (`app/main.py`)

Registered in the FastAPI app to catch `ServiceException` and return consistent responses:

```python
@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
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
```

### 3. Response Model (`app/models/service.py`)

Configured to exclude null/None fields from serialization:

```python
class Response(BaseModel, Generic[T]):
    model_config = ConfigDict(exclude_none=True)

    code: int
    message: str
    data: T | None = None
```

## Response Formats

### Success Response (with data)

**HTTP Status:** 200

```json
{
  "code": 200,
  "message": "File retrieved successfully",
  "data": {
    "file_id": "abc123",
    "filename": "document.pdf",
    "size": 1024
  }
}
```

### Success Response (without data)

**HTTP Status:** 200

```json
{
  "code": 200,
  "message": "Success"
}
```

Note: The `data` field is **omitted** when null, not set to `null`.

### Error Response

**HTTP Status:** 404 (varies by error)

```json
{
  "code": 404,
  "message": "File not found"
}
```

Note: The `data` field is **omitted** from error responses.

## Usage in Routes

### Raising ServiceException

```python
from app.exceptions import ServiceException
from fastapi import status

@router.get("/{file_id}")
async def get_file(self, file_id: str):
    try:
        data = await self.file_service.get_file(file_id)
        return {
            "code": status.HTTP_200_OK,
            "message": "File retrieved successfully",
            "data": data
        }
    except S3Error as e:
        match e.code:
            case "NoSuchKey":
                raise ServiceException(
                    code=status.HTTP_404_NOT_FOUND,
                    message="File not found"
                )
            case "AccessDenied":
                raise ServiceException(
                    code=status.HTTP_403_FORBIDDEN,
                    message="Access denied to storage"
                )
            case _:
                raise ServiceException(
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Storage error: {e.code}"
                )
```

## HTTP Status Codes Mapping

| Error Type | HTTP Status | Code | Message |
|------------|-------------|------|---------|
| File not found | 404 | 404 | "File not found" |
| Access denied | 403 | 403 | "Access denied to storage" |
| Invalid input | 400 | 400 | "Invalid file identifier" |
| Server error | 500 | 500 | "Storage error: ..." |
| Unexpected | 500 | 500 | "Unexpected error: ..." |

## Benefits

1. **Consistent Format**: All responses (success and error) use the same structure
2. **Proper HTTP Semantics**: Correct HTTP status codes in headers
3. **Clean JSON**: Null fields are omitted, not set to `null`
4. **Type Safety**: Uses Pydantic models for validation
5. **Centralized**: One place to handle all service exceptions

## Error Handling Flow

```
1. Client calls endpoint
   ↓
2. Service layer encounters error
   ↓
3. Service raises S3Error or Exception
   ↓
4. Router catches exception
   ↓
5. Router raises ServiceException
   ↓
6. FastAPI catches ServiceException
   ↓
7. Custom handler returns JSONResponse
   ↓
8. Client receives consistent error format
```

## Example API Calls

### Success Case

```bash
curl http://localhost:8000/files/abc123

# Response: HTTP 200
{
  "code": 200,
  "message": "File retrieved successfully",
  "data": {
    "file_id": "abc123",
    "filename": "test.pdf"
  }
}
```

### Error Case

```bash
curl http://localhost:8000/files/invalid

# Response: HTTP 404
{
  "code": 404,
  "message": "File not found"
}
```

## Adding New Error Types

To add a new error type:

1. Catch the exception in your route
2. Raise `ServiceException` with appropriate code and message
3. The handler automatically formats the response

```python
except CustomError as e:
    raise ServiceException(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Custom error message",
        data={"details": "optional error details"}  # Optional
    )
```
