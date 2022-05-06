from fastapi import APIRouter

from .classroom import classroom_router
from .room_posts import room_posts_router


router = APIRouter(
    tags=['classroom'],
)

router.include_router(router=classroom_router, prefix='/room')
router.include_router(router=room_posts_router, prefix='/room_posts')
