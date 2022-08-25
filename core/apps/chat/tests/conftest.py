import pytest

from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.tests.conftest import *  # noqa


@pytest.fixture
def dialog_repository():
    return DialogRepository()
