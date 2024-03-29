from typing import Dict

from core.apps.users.models import User


class AuthorMixin:
    def __init__(self, user: User, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

    async def validate(self, attrs: Dict) -> Dict:
        attrs['author_id'] = self.user.id
        attrs['updated_by_id'] = self.user.id

        return await super().validate(attrs)
