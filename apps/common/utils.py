from datetime import datetime

from pydantic import BaseModel

from apps.user.schemas import AuthorSchema


def get_current_datetime():
    # TODO: настроить таймзон
    return datetime.utcnow()


# TODO: выпилить
def get_author_data(user) -> BaseModel:
    return AuthorSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
    )


def prepare_json_schema(schema: BaseModel):
    """Workaround to escape the JSONDecode error."""
    base_dict = schema.dict()

    for key in base_dict:
        if isinstance(base_dict[key], datetime):
            base_dict[key] = base_dict[key].isoformat()
    return base_dict


def prepare_json_list(schemas: list[BaseModel]):
    """Workaround to escape the JSONDecode error for list of schemas."""
    return [prepare_json_schema(schema) for schema in schemas]
