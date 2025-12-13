from typing import Any, Optional


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
        super().__init__(message)
