from fastapi.exceptions import HTTPException

from starlette import status

from common.config import config


class UserException(HTTPException):
    pass


class NotAuthenticatedException(UserException):
    def __init__(self, detail = None, headers = None) -> None:
        status_code = status.HTTP_401_UNAUTHORIZED
        detail = detail or config.USER_PERMISSION_DENIED_ERROR

        super().__init__(status_code, detail, headers)