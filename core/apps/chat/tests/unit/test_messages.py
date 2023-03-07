from datetime import datetime

import pytest

from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.apps.chat.repositories.message_repository import MessageRepository
from core.apps.chat.schemas import MessageCreateSchema
from core.apps.chat.services.message_service import MessageService
from core.tests.factories.chat.dialog import DialogFactory
from core.tests.factories.chat.message import MessageFactory
from core.tests.factories.user.user import UserFactory


@pytest.mark.asyncio
async def test_send_message_success(
    dialog_repository: DialogRepository,
    message_repository: MessageRepository,
    message_service: MessageService,
):
    sender = await UserFactory.create()
    dialog = await DialogFactory.create(participants=[sender, await UserFactory.create()])
    message_text = 'hello world'

    message, errors = await message_service.create(
        MessageCreateSchema(
            sender_id=sender.id,
            text=message_text,
            dialog_id=dialog.id,
        ),
        join=['sender', 'dialog'],
    )

    assert message
    assert not errors
    assert await message_repository.count()
    assert message.sender_id == sender.id, message.sender
    assert message.text == message_text, message.text
    assert message.dialog_id == dialog.id, message.dialog

    dialog = await dialog_repository.retrieve(id=message.dialog_id, join=['messages'])
    assert len(dialog.messages) == 1, dialog.messages


@pytest.mark.asyncio
async def test_send_message_empty_dialog(
    message_repository: MessageRepository,
    message_service: MessageService,
):
    sender = await UserFactory.create()
    dialog = await DialogFactory.create(
        participants=[
            await UserFactory.create(),
            await UserFactory.create(),
        ],
    )
    message_text = 'hello world'

    message, errors = await message_service.create(
        MessageCreateSchema(
            sender_id=sender.id,
            text=message_text,
            dialog_id=dialog.id,
        ),
        join=['sender', 'dialog'],
    )

    assert not message
    assert errors
    assert 'dialog_id' in errors
    assert not await message_repository.count()


@pytest.mark.asyncio
async def test_get_unique_last_messages(
    message_service: MessageService,
):
    actor = await UserFactory.create()
    sender = await UserFactory.create()
    first_dialog = await DialogFactory.create(participants=[actor, sender], id=3)
    last_dialog = await DialogFactory.create(participants=[actor, await UserFactory.create()], id=4)
    await DialogFactory.create(participants=[sender, await UserFactory.create()])  # ignored dialog

    ignored_message_text = 'ignored message'
    # ignored message
    await MessageFactory(
        dialog=first_dialog,
        sender=actor,
        text=ignored_message_text,
    )

    first_message_text = 'first unignored message'
    first_message = await MessageFactory.create(
        dialog=first_dialog,
        sender=actor,
        text=first_message_text,
    )

    last_message_text = 'unignored message from another dialog'
    last_message = await MessageFactory.create(
        created_at=datetime.utcnow(),
        dialog=last_dialog,
        sender=sender,
        text=last_message_text,
    )
    messages = await message_service.get_unique_last_messages(
        user_id=actor.id,
        join=['sender'],
    )

    assert len(messages) == 2, messages
    assert last_message.id == messages[0].id
    assert first_message.id == messages[1].id
