from fastapi import (
    APIRouter,
    Request,
)
from fastapi.exceptions import HTTPException

from starlette import status

from core.apps.localization.schemas import ChangeLocalizationSchema
from core.apps.localization.services import LocalizationService


router = APIRouter(tags=['localization'])


@router.put(
    '',
    response_model=ChangeLocalizationSchema,
    operation_id='changeLocalization',
)
async def change_localization(request: Request, schema: ChangeLocalizationSchema):
    _, errors = await LocalizationService.set_localization_to_client(
        schema.language_code,
        request.client.host,
    )

    if errors is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return schema
