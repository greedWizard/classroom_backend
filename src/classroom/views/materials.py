from typing import List, Optional, TypedDict

from fastapi import APIRouter, Depends, UploadFile, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, paginate

from starlette import status
from attachment.schemas import AttachmentCreateSchema, AttachmentDeleteSchema, AttachmentListItemSchema

from attachment.services.attachment_service import AttachmentService

from classroom.schemas import (
    MaterialCreateSchema,
    MaterialCreateSuccessSchema,
    MaterialDeleteSchema,
    MaterialDetailSchema,
    MaterialListItemSchema,
    MaterialUpdateSchema,
)
from classroom.services.material_service import MaterialService
from classroom.services.room_service import ParticipationService, RoomService

from core.config import config
from core.utils import get_author_data
from user.exceptions import NotAuthenticatedException

from user.models import User
from user.schemas import AuthorSchema
from user.utils import get_current_user


materials_router = APIRouter()

@materials_router.post(
    '',
    response_model=MaterialCreateSuccessSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='createMaterial',
)
async def create_new_material(
    materialCreateSchema: MaterialCreateSchema,
    user: User = Depends(get_current_user),
):
    material_service = MaterialService(user)
    material, errors = await material_service.create(materialCreateSchema)

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return MaterialCreateSuccessSchema(
        id=material.id,
        title=material.title,
        description=material.description,
        text=material.text,
        room_id=material.room_id,
        author_id=material.author_id,
    )


@materials_router.get(
    '',
    response_model=Page[MaterialListItemSchema],
    status_code=status.HTTP_200_OK,
    operation_id='getMaterials',
)
async def get_materials(
    room_id: int,
    user: User = Depends(get_current_user),
    ordering: List[str] = Query(['-created_at']),
):
    if not await user.is_participating(room_id=room_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not participating in this room')

    material_service = MaterialService(user)
    materials, errors = await material_service.fetch(
        {
            'room_id': room_id,
        },
        _ordering=ordering,
        _select_related=['author']
    )

    if errors:
        raise HTTPException(status=status.HTTP_400_BAD_REQUEST, detail=errors)
    return paginate([MaterialListItemSchema.from_orm(material) for material in materials])


@materials_router.put(
    '/{material_id}',
    response_model=MaterialListItemSchema,
    status_code=status.HTTP_200_OK,
)
async def update_material(
    material_id: int,
    materialUpdateSchema: MaterialUpdateSchema,
    user: User = Depends(get_current_user),
):
    material_service = MaterialService(user)
    material, errors = await material_service.update(
        material_id,
        materialUpdateSchema,
        fetch_related=['author'],
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return MaterialListItemSchema.from_orm(material)


@materials_router.get(
    '/{material_id}',
    response_model=MaterialDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_material(
    material_id: int,
    user: User = Depends(get_current_user),
):
    material_service = MaterialService(user)
    material, errors = await material_service.retrieve(['author', 'attachments'], id=material_id)

    if errors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=errors)
    return MaterialDetailSchema(
        title=material.title,
        room_id=material.room_id,
        description=material.description,
        id=material.id,
        text=material.text,
        author=AuthorSchema.from_orm(material.author),
        attachments=[
            AttachmentListItemSchema.from_orm(attachment) \
                for attachment in await material.attachments
        ],
        created_at=material.created_at,
        updated_at=material.updated_at,
    ) 


@materials_router.post(
    '/{material_id}/attachments',
    response_model=MaterialDetailSchema,
    status_code=status.HTTP_201_CREATED,
)
async def attach_files_to_material(
    material_id: int,
    attachments: List[UploadFile],
    user: User = Depends(get_current_user),
):
    attachments_list = []
    attachment_service = AttachmentService(user)

    for attachment in attachments:
        attachments_list.append(
            AttachmentCreateSchema(
                filename=attachment.filename,
                source=await attachment.read()
            )
        )
    material, errors = await attachment_service.create_for_material(
        attachments_list, material_id,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return MaterialDetailSchema(
        title=material.title,
        room_id=material.room_id,
        description=material.description,
        id=material.id,
        text=material.text,
        author=AuthorSchema.from_orm(material.author),
        attachments=[
            AttachmentListItemSchema.from_orm(attachment) \
                for attachment in await material.attachments
        ],
        created_at=material.created_at,
        updated_at=material.updated_at,
    )


@materials_router.delete(
    '',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def bulk_delete_materials(
    materialDeleteSchema: MaterialDeleteSchema,
    user: User = Depends(get_current_user),
):
    material_service = MaterialService(user)
    errors = await material_service.bulk_delete(**materialDeleteSchema.dict(exclude_unset=True))

    if errors:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=errors)


@materials_router.delete(
    '/{material_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='deleteMaterial',
)
async def delete_material(
    material_id: int,
    user: User = Depends(get_current_user),
):
    material_service = MaterialService(user)
    success = await material_service.delete_by_id(material_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Operation not allowed')
