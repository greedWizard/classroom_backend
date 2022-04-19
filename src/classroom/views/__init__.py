from fastapi import APIRouter

from .classroom import classroom_router
from .materials import materials_router


router = APIRouter(
    tags=['classroom'],
)

router.include_router(router=classroom_router, prefix='/room')
router.include_router(router=materials_router, prefix='/materials')
