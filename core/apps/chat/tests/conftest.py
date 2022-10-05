import pytest

from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.apps.chat.repositories.message_repository import MessageRepository
from core.apps.chat.services.message_service import MessageService
from core.tests.conftest import *  # noqa


@pytest.fixture
def dialog_repository():
    return DialogRepository()


@pytest.fixture
def message_service():
    return MessageService()


@pytest.fixture
def message_repository():
    return MessageRepository()
