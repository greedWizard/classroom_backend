import hashlib
from typing import (
    Any,
    Optional,
)

from dependency_injector.wiring import (
    inject,
    Provide,
)
from itsdangerous import TimedSerializer

from apps.common.config import config
from apps.common.containers import MainContainer


def hash_string(string: str):
    return hashlib.md5(string.encode()).hexdigest()


@inject
async def unsign_timed_token(
    token: str,
    salt: Optional[str] = None,
    timed_serializer: TimedSerializer = Provide[MainContainer.timed_serializer],
) -> Any:
    """Method returns value from signed token."""
    return timed_serializer.loads(
        token,
        max_age=config.RESET_PASSWORD_TIMEDELTA.total_seconds(),
        salt=salt,
    )
