from fastapi.security import OAuth2PasswordBearer

from core.common.config import config


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=config.OUATH2_TOKEN_URL)
