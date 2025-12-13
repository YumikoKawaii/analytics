from fastapi import UploadFile
from typing import Dict, Any
from app.packages import minio_client, redis_client, MinioClient, RedisClient, FileStat
import hashlib
from datetime import datetime, UTC


class FileService:
    _minio: MinioClient
    _redis: RedisClient

    def __init__(self):
        self._minio = minio_client
        self._redis = redis_client

    async def save_file(self, file: UploadFile) -> Dict[str, Any]:
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        file_id = f"{file_hash[:16]}"

        upload_result = self._minio.upload_file(
            object_name=file_id,
            data=contents,
            content_type=file.content_type or "application/octet-stream",
            metadata={
                "original_filename": file.filename or "unknown",
                "upload_timestamp": datetime.now(UTC).isoformat()
            }
        )

        file_metadata = {
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents),
            "etag": upload_result["etag"],
            "status": "uploaded",
            "upload_timestamp": datetime.now(UTC).isoformat()
        }

        return file_metadata

    async def get_file(self, file_id: str) -> FileStat:
        return self._minio.stat_file(file_id)

    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        self._minio.delete_file(file_id)

        return {
            "file_id": file_id,
            "status": "deleted",
        }

    async def list_files(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        all_files = self._minio.list_files()
        total = len(all_files)
        paginated_files = all_files[skip:skip + limit]

        return {
            "files": paginated_files,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
