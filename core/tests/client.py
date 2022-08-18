from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from core.apps.users.models import User


class FastAPITestClient(TestClient):
    def authorize(self, user: User):
        auth_jwt = AuthJWT()
        auth_token = auth_jwt.create_access_token(subject=user.id)
        self.headers.update({'Authorization': f'Bearer {auth_token}'})
