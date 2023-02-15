from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.common.config import config


router = APIRouter(tags=['certbot'])


@router.get(
    '/{file_name}',
    summary='Proxies certbot directory to prove ssl-certificate',
)
def return_cerbot_file(file_name: str):
    return FileResponse(path=config.WELL_KNOWN_PATH.format(file_name=file_name))
