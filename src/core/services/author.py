from typing import Dict

from user.models import User


class AuthorMixin:
    def __init__(self, user: User, *args, **kwargs) -> None:
        self.user = user
        super().__init__(*args, **kwargs)

    async def validate(self, attrs: Dict) -> Dict:
        attrs['author_id'] = self.user.id
        attrs['updated_by_id'] = self.user.id

        return await super().validate(attrs)
