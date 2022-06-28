from fastapi import APIRouter

from .assignments import router as assignments_router
from .classroom import classroom_router
from .participations import participations_router
from .room_posts import room_posts_router


router = APIRouter()

router.include_router(router=classroom_router, prefix='/room', tags=['room'])
router.include_router(router=room_posts_router, prefix='/room_post', tags=['roomPost'])
router.include_router(
    router=participations_router,
    prefix='/participation',
    tags=['participation'],
)
router.include_router(
    router=assignments_router,
    prefix='/homework-assignment',
    tags=['assignment'],
)
