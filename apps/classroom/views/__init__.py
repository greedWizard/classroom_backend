from fastapi import APIRouter

from .classroom import classroom_router
from .homework_assignments import router as homework_assignments_router
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
    router=homework_assignments_router,
    prefix='/homework-assignment',
    tags=['assignment'],
)
