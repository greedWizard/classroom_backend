from fastapi import Request
from fastapi.responses import JSONResponse

from fastapi_jwt_auth.exceptions import AuthJWTException, InvalidHeaderError

from starlette import status


def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message}
    )