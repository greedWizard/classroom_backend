from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette import status

from fastapi import Request
from fastapi.responses import JSONResponse


def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': exc.message},
    )
