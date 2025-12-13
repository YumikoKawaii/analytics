import datetime

from minio import Minio
from minio.datatypes import Object
from minio.error import S3Error
from typing import BinaryIO, Optional
from io import BytesIO

from pydantic import BaseModel

from app.packages.infrastructure.minio import minio_cli

from app.config import settings


class FileStat(BaseModel):
    bucket_name: str
    object_name: str
    size: int
    etag: str
    last_modified: datetime.datetime
    content_type: str

    @classmethod
    def from_object(cls, obj: Object):
        return cls(
            bucket_name=obj.bucket_name,
            object_name=obj.object_name,
            size=obj.size,
            etag=obj.etag,
            last_modified=obj.last_modified,
            content_type=obj.content_type,
        )


class MinioClient:
    client: Minio
    bucket_name: str

    def __init__(self):
        self.bucket_name = settings.minio_bucket
        self._initialize()

    def _initialize(self):
        self.client = minio_cli
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise Exception(f"Failed to create bucket: {e}")

    def upload_file(
            self,
            object_name: str,
            data: bytes | BinaryIO,
            content_type: str = "application/octet-stream",
            metadata: Optional[dict] = None
    ) -> dict:
        if isinstance(data, bytes):
            data_stream = BytesIO(data)
            length = len(data)
        else:
            data.seek(0, 2)
            length = data.tell()
            data.seek(0)
            data_stream = data

        result = self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=data_stream,
            length=length,
            content_type=content_type,
            metadata=metadata
        )

        return {
            "bucket": result.bucket_name,
            "object_name": result.object_name,
            "etag": result.etag,
            "version_id": result.version_id,
            "url": self.get_object_url(object_name)
        }

    def download_file(self, object_name: str) -> bytes:
        response = self.client.get_object(self.bucket_name, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data

    def delete_file(self, object_name: str) -> bool:
        self.client.remove_object(self.bucket_name, object_name)
        return True

    def file_exists(self, object_name: str) -> bool:
        self.client.stat_object(self.bucket_name, object_name)
        return True

    def get_object_url(self, object_name: str) -> str:
        protocol = "https" if settings.minio_secure else "http"
        return f"{protocol}://{settings.minio_endpoint}/{self.bucket_name}/{object_name}"

    def get_presigned_url(self, object_name: str, expires_in_seconds: int = 3600) -> str:
        from datetime import timedelta
        url = self.client.presigned_get_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            expires=timedelta(seconds=expires_in_seconds)
        )
        return url

    def list_files(self, prefix: str = "") -> list[FileStat]:
        objects = self.client.list_objects(
            bucket_name=self.bucket_name,
            prefix=prefix,
            recursive=True
        )

        files = []
        for obj in objects:
            files.append(FileStat.from_object(obj))

        return files

    def stat_file(self, object_name: str) -> FileStat:
        return FileStat.from_object(self.client.stat_object(self.bucket_name, object_name))


minio_client = MinioClient()
