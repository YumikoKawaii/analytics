# Infrastructure Setup

This document describes how to set up and use the Redis and MinIO infrastructure.

## Starting Infrastructure

Start Redis and MinIO using Docker Compose:

```bash
docker-compose -f infrastructure.docker-compose.yaml up -d
```

Stop services:

```bash
docker-compose -f infrastructure.docker-compose.yaml down
```

Stop services and remove volumes (⚠️ deletes all data):

```bash
docker-compose -f infrastructure.docker-compose.yaml down -v
```

## Services

### Redis
- **Host**: localhost:6379
- **Purpose**: Caching and session storage
- **Console**: N/A (use redis-cli)

### MinIO
- **API**: http://localhost:9000
- **Console**: http://localhost:9001
- **Username**: minioadmin
- **Password**: minioadmin
- **Purpose**: Object storage (S3-compatible)

## Configuration

Configure services via environment variables in `.env`:

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_DECODE_RESPONSES=true

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=analytics
```

## Usage

### Redis Client

```python
from app.packages import redis_client

# Basic operations
redis_client.set("key", "value", ex=3600)  # Set with 1-hour expiration
value = redis_client.get("key")

# JSON operations
redis_client.set_json("user:123", {"name": "John", "age": 30}, ex=3600)
user = redis_client.get_json("user:123")

# Counter operations
redis_client.incr("page_views")
redis_client.decr("stock_count", amount=5)

# Expiration
redis_client.expire("key", 300)  # 5 minutes
ttl = redis_client.ttl("key")

# Check existence
if redis_client.exists("key"):
    print("Key exists")

# Delete
redis_client.delete("key1", "key2", "key3")
```

### MinIO Client

```python
from app.packages import minio_client

# Upload file
with open("file.pdf", "rb") as f:
    result = minio_client.upload_file(
        object_name="documents/file.pdf",
        data=f,
        content_type="application/pdf",
        metadata={"user_id": "123"}
    )
    print(result["url"])

# Upload bytes
data = b"Hello, World!"
result = minio_client.upload_file(
    object_name="text/hello.txt",
    data=data,
    content_type="text/plain"
)

# Download file
file_data = minio_client.download_file("documents/file.pdf")
with open("downloaded.pdf", "wb") as f:
    f.write(file_data)

# Check if file exists
if minio_client.file_exists("documents/file.pdf"):
    print("File exists")

# Get presigned URL (temporary access)
url = minio_client.get_presigned_url(
    object_name="documents/file.pdf",
    expires_in_seconds=3600  # 1 hour
)

# List files
files = minio_client.list_files(prefix="documents/")
for file in files:
    print(f"{file['object_name']}: {file['size']} bytes")

# Delete file
minio_client.delete_file("documents/file.pdf")
```

### Using in Services

Example: File upload with MinIO storage and Redis caching

```python
from app.packages import minio_client, redis_client
from fastapi import UploadFile

async def save_file(file: UploadFile, user_id: str):
    # Generate unique filename
    object_name = f"uploads/{user_id}/{file.filename}"

    # Upload to MinIO
    contents = await file.read()
    result = minio_client.upload_file(
        object_name=object_name,
        data=contents,
        content_type=file.content_type
    )

    # Cache file metadata in Redis
    file_metadata = {
        "filename": file.filename,
        "url": result["url"],
        "size": len(contents),
        "content_type": file.content_type,
        "user_id": user_id
    }
    redis_client.set_json(
        f"file:{result['etag']}",
        file_metadata,
        ex=86400  # Cache for 24 hours
    )

    return file_metadata
```

## Lazy Initialization

Both clients use lazy initialization by default:
- Connection is established only when first used
- Safe to import even when services are not running
- Import errors won't occur at module load time

To force immediate connection:

```python
from app.packages.storage import MinioClient
from app.packages.cache import RedisClient

minio = MinioClient(lazy=False)  # Connect immediately
redis = RedisClient(lazy=False)  # Connect immediately
```

## Health Checks

Both services have health check endpoints configured in docker-compose:

- **Redis**: `redis-cli ping`
- **MinIO**: `http://localhost:9000/minio/health/live`

Check service health:

```bash
# Redis
docker exec analytics-redis redis-cli ping

# MinIO
curl http://localhost:9000/minio/health/live
```

## Troubleshooting

### Connection Refused
- Ensure services are running: `docker ps`
- Check ports are not in use: `lsof -i :6379` and `lsof -i :9000`

### MinIO Bucket Not Found
- The bucket is created automatically on first use
- Check MinIO console at http://localhost:9001

### Redis Connection Timeout
- Verify Redis is accepting connections: `docker logs analytics-redis`
- Check firewall settings

## Data Persistence

Both services use Docker volumes for data persistence:
- `redis-data`: Redis database files
- `minio-data`: MinIO object storage

Data persists across container restarts unless volumes are explicitly removed.
