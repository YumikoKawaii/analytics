from typing import TypeVar, Generic
from fastapi import File, UploadFile, status
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None

    @classmethod
    def success(cls, data: T, message: str = "Success"):
        return cls(
            code=status.HTTP_200_OK,
            message=message,
            data=data,
        )

    @classmethod
    def error(cls, code: int, message: str):
        return cls(
            code=code,
            message= message,
        )

class UploadFileRequest:
    file: UploadFile

    def __init__(self, file: UploadFile = File(...)):
        self.file = file


class GetFileRequest:
    file_id: str

    def __init__(self, file_id: str):
        self.file_id = file_id
