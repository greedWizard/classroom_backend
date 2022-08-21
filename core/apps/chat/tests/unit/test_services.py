import pytest

from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.apps.chat.services.dialog_service import DialogService
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.tests.factories.chat.dialog import DialogFactory
from core.tests.factories.classroom.participation import ParticipationFactory
from core.tests.factories.classroom.room import RoomFactory


@pytest.mark.asyncio
async def test_dialog_add_participants(
    dialog_repository: DialogRepository,
):
    assert not await dialog_repository.count()

    participation = await ParticipationFactory.create()
    new_participation = await ParticipationFactory.create(room=participation.room)

    dialog_service = DialogService()
    dialog = await DialogFactory.create()

    await dialog_service._add_participants_to_dialog(
        dialog_id=dialog.id,
        participants_ids=[participation.user_id, new_participation.user_id],
    )
    dialog = await dialog_repository.refresh(
        dialog,
        join=['participants'],
    )
    assert dialog.participants_count == 2, dialog.participants_count
    assert await dialog_repository.count(participants_count=2)


@pytest.mark.asyncio
async def test_dialog_add_many_participants(
    dialog_repository: DialogRepository,
):
    assert not await dialog_repository.count()

    room = await RoomFactory.create()
    participants_count = 30
    new_participations = await ParticipationFactory.create_batch(
        size=participants_count,
        room=room,
    )

    dialog_service = DialogService()
    dialog = await DialogFactory.create()

    await dialog_service._add_participants_to_dialog(
        dialog_id=dialog.id,
        participants_ids=[
            new_participation.user_id for new_participation in new_participations
        ],
    )
    dialog = await dialog_repository.refresh(
        dialog,
        join=['participants'],
    )
    assert dialog.participants_count == participants_count, dialog.participants_count
    assert await dialog_repository.count(participants_count=participants_count)


@pytest.mark.asyncio
async def test_dialog_add_same_users(
    dialog_repository: DialogRepository,
):
    assert not await dialog_repository.count()

    room = await RoomFactory.create()
    participants_count = 2
    new_participations = await ParticipationFactory.create_batch(
        size=participants_count,
        room=room,
    )

    dialog_service = DialogService()
    dialog = await DialogFactory.create()

    await dialog_service._add_participants_to_dialog(
        dialog_id=dialog.id,
        participants_ids=[
            new_participation.user_id for new_participation in new_participations
        ],
    )
    await dialog_service._add_participants_to_dialog(
        dialog_id=dialog.id,
        participants_ids=[
            new_participation.user_id for new_participation in new_participations
        ],
    )
    assert await dialog_repository.count(participants_count=participants_count)
    assert not await dialog_repository.count(participants_count=participants_count * 2)


# TODO: перенести в тесты participations
@pytest.mark.asyncio
async def test_user_roommates_participants(
    participation_repository: ParticipationRepository,
):
    participation = await ParticipationFactory.create()
    await ParticipationFactory.create_batch(size=10, user=participation.user)

    room_mates_count = 5
    new_participations = await ParticipationFactory.create_batch(
        size=room_mates_count,
        room=participation.room,
    )
    new_participations_ids = [participation.user_id for participation in new_participations]

    actual_roommates = await participation_repository.get_user_roommates(
        user_id=participation.user_id,
    )
    assert sorted(new_participations_ids) == sorted(actual_roommates)


@pytest.mark.asyncio
async def test_user_roommates_empty_room(
    participation_repository: ParticipationRepository,
):
    participation = await ParticipationFactory.create()
    await ParticipationFactory.create_batch(size=10, user=participation.user)

    actual_roommates = await participation_repository.get_user_roommates(
        user_id=participation.user_id,
    )
    assert not actual_roommates


@pytest.mark.asyncio
async def test_are_users_roommates(
    participation_repository: ParticipationRepository,
):
    room = await RoomFactory.create()
    new_participations = await ParticipationFactory.create_batch(size=13, room=room)
    rommates_ids = [new_participation.user_id for new_participation in new_participations]
    assert await participation_repository.are_users_rommmates(users_ids=rommates_ids)


@pytest.mark.asyncio
async def test_dialog_init_success(
    dialog_repository: DialogRepository,
):
    assert not await dialog_repository.count()

    participation = await ParticipationFactory.create()
    room_mates_count = 5
    new_participations = await ParticipationFactory.create_batch(
        size=room_mates_count,
        room=participation.room,
    )
    new_participations_ids = [participation.user_id for participation in new_participations]
    dialog_participants_ids = [participation.user_id] + new_participations_ids

    dialog_service = DialogService()

    dialog, errors = await dialog_service.initialize_dialog(
        users_ids=dialog_participants_ids,
        author_id=participation.user_id,
        join=['participants'],
    )

    assert not errors
    assert dialog.participants_count == len(dialog_participants_ids), dialog.participants_count
    assert await dialog_repository.count(participants_count=len(dialog_participants_ids)) == 1


@pytest.mark.asyncio
async def test_dialog_repository_find_exact_dialog(
    dialog_repository: DialogRepository,
):
    room = await RoomFactory.create()
    old_participants = await ParticipationFactory.create_batch(2, room=room)
    old_participants_users = [participant.user for participant in old_participants]
    new_participants = await ParticipationFactory.create_batch(2, room=room)
    new_participants_users = [
        participant.user for participant in old_participants + new_participants
    ]

    unmatch_dialog = await DialogFactory.create(
        participants=new_participants_users,
    )
    match_dialog = await DialogFactory.create(
        participants=old_participants_users,
    )

    check_dialog = await dialog_repository.find_exact_dialog(
        users_ids=[user.id for user in old_participants_users],
    )
    assert check_dialog.id == match_dialog.id

    check_dialog = await dialog_repository.find_exact_dialog(
        users_ids=[user.id for user in new_participants_users],
    )
    assert check_dialog.id == unmatch_dialog.id

    check_dialog = await dialog_repository.find_exact_dialog(
        users_ids=[
            user.id for user in new_participants_users[1:] + old_participants_users[1:]
        ],
    )
    assert not check_dialog


@pytest.mark.asyncio
async def test_dialog_start_success(
    dialog_repository: DialogRepository,
):
    dialog_service = DialogService()
    dialogs_count = await dialog_repository.count()

    assert not dialogs_count

    participation = await ParticipationFactory.create()
    roommate = await ParticipationFactory.create(room=participation.room)

    dialog, errors = await dialog_service.start_dialog(
        participants_ids=[roommate.user_id],
        author_id=participation.user_id,
        join=['participants'],
    )

    assert not errors
    assert dialog.participants_count == 2

    dialog_participants_ids = [participant.id for participant in dialog.participants]

    assert roommate.user_id in dialog_participants_ids
    assert participation.user_id in dialog_participants_ids


@pytest.mark.asyncio
async def test_dialog_start_not_roommates(
    dialog_repository: DialogRepository,
):
    participations = await ParticipationFactory.create_batch(
        size=3,
    )
    random_particaiptions_users = [participation.user for participation in participations]

    dialog_service = DialogService()
    dialog_author = random_particaiptions_users.pop(0)

    dialog, errors = await dialog_service.start_dialog(
        participants_ids=[user.id for user in random_particaiptions_users],
        author_id=dialog_author.id,
    )

    assert not dialog
    assert errors == {'error': 'Users are not rommates.'}, errors
