# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Python 3.12+ with virtual environment activated

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Infrastructure

Start Redis and MinIO services:

```bash
docker-compose -f infrastructure.docker-compose.yaml up -d
```

Verify services are running:

```bash
docker ps
```

You should see:
- `analytics-redis` running on port 6379
- `analytics-minio` running on ports 9000 (API) and 9001 (Console)

### 3. Access MinIO Console (Optional)

Open browser to: http://localhost:9001

- Username: `minioadmin`
- Password: `minioadmin`

### 4. Start the Application

```bash
python main.py
```

The API will be available at: http://localhost:8000

### 5. Test File Upload

Using curl:

```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.pdf"
```

Using Python:

```python
import requests

with open("test.txt", "rb") as f:
    response = requests.post(
        "http://localhost:8000/files/upload",
        files={"file": f}
    )
    print(response.json())
```

### 6. View API Documentation

Open browser to: http://localhost:8000/docs

## What Happens When You Upload a File

1. **File is uploaded** via POST to `/files/upload`
2. **MinIO stores** the file with a unique name
3. **Redis caches** the file metadata for 24 hours
4. **Response returns** file information including:
   - File ID
   - URL
   - Size
   - Content type
   - Upload timestamp

## Stopping Services

### Stop Application
Press `Ctrl+C` in the terminal running the app

### Stop Infrastructure

```bash
# Stop services (keeps data)
docker-compose -f infrastructure.docker-compose.yaml down

# Stop and remove data
docker-compose -f infrastructure.docker-compose.yaml down -v
```

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       v
┌─────────────────────┐
│   FastAPI App       │
│  (Port 8000)        │
└─────────┬───────────┘
          │
          ├──────────┐
          │          │
          v          v
    ┌─────────┐  ┌─────────┐
    │  Redis  │  │  MinIO  │
    │  :6379  │  │  :9000  │
    └─────────┘  └─────────┘
     (Cache)     (Storage)
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :6379  # Redis
lsof -i :9000  # MinIO

# Kill process
kill -9 <PID>
```

### Docker Services Not Starting

```bash
# Check logs
docker logs analytics-redis
docker logs analytics-minio

# Restart services
docker-compose -f infrastructure.docker-compose.yaml restart
```

### Connection Errors

Make sure services are running:

```bash
# Check Redis
docker exec analytics-redis redis-cli ping
# Should return: PONG

# Check MinIO
curl http://localhost:9000/minio/health/live
# Should return: OK
```

## Next Steps

- Read [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for detailed client usage
- Explore the API at http://localhost:8000/docs
- Configure environment variables in `.env`
- Add database for persistent metadata storage
