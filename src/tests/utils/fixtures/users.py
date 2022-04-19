import asyncio
from datetime import datetime
import hashlib
import uuid

from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from starlette import status

import pytest

from tests.utils.fixtures import client, event_loop, fake, app

from user.models import User


@pytest.fixture
def authentication_token(
    event_loop: asyncio.AbstractEventLoop,
    fake: Faker,
    app: FastAPI,
    client: TestClient
) -> str:
    password = '123'
    default_user_data = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': f'+70000000000',
        'password': hashlib.md5(password.encode()).hexdigest(),
        'activation_token': uuid.uuid4().hex,
        'email': fake.email(),
        'activation_deadline_dt': datetime.utcnow(),
        'is_active': True,
    }

    user, _ = event_loop.run_until_complete(
        User.get_or_create(
            defaults=default_user_data,
        )
    )
    
    url = app.url_path_for('authenticate_user')
    response = client.post(url, json={
        'email': user.email,
        'password': '123',
    })
    assert response.status_code == status.HTTP_200_OK

    yield response.json()['access_token']
