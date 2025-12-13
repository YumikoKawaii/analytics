from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from minio.error import S3Error

from app.models.service import Response, UploadFileRequest, GetFileRequest
from app.packages import FileStat
from app.services.file_service import FileService
from app.exceptions import ServiceException

router = APIRouter(prefix="/files", tags=["Files"])

@cbv(router)
class FileHandler:
    def __init__(self):
        self.file_service = FileService()

    @router.post("/upload", status_code=status.HTTP_200_OK, response_model=Response)
    async def upload_file(self, request: UploadFileRequest = Depends()):
        data = await self.file_service.save_file(request.file)
        return Response.success(data)

    @router.get("/{file_id}", response_model=Response[FileStat])
    async def get_file(self, request: GetFileRequest = Depends()):
        try:
            data = await self.file_service.get_file(request.file_id)
            return Response.success(jsonable_encoder(data))
        except S3Error as e:
            match e.code:
                case "NoSuchKey":
                    raise ServiceException(
                        code=status.HTTP_404_NOT_FOUND,
                        message="File not found"
                    )
                case _:
                    raise ServiceException(
                        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message=f"Storage error: {e.code}"
                    )
        except Exception as e:
            raise ServiceException(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error: {str(e)}"
            )

    @router.delete("/{file_id}", status_code=status.HTTP_200_OK, response_model=Response)
    async def delete_file(self, file_id: str):
        data = await self.file_service.delete_file(file_id)
        return {
            "code": status.HTTP_200_OK,
            "message": "File deleted successfully",
            "data": data
        }

    @router.get("/list", status_code=status.HTTP_200_OK, response_model=Response)
    async def list_files(self, skip: int = 0, limit: int = 10):
        data = await self.file_service.list_files(skip=skip, limit=limit)
        return {
            "code": status.HTTP_200_OK,
            "message": "Files retrieved successfully",
            "data": data
        }
