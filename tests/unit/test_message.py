from uuid import UUID

import pytest

from notification_registry import NotificationChannel
from notification_registry import NotificationMetadata
from notification_registry import NotificationPriority
from notification_registry import NotificationType
from tests.conftest import build_message


def test_notification_id_auto_populated(notification_metadata):
    assert notification_metadata.notification_id is not None
    assert isinstance(notification_metadata.notification_id, UUID)


def test_notification_id_unique_per_instance():
    m1 = NotificationMetadata(
        notification_type=NotificationType.RESET_PASSWORD,
        channel=NotificationChannel.EMAIL,
    )
    m2 = NotificationMetadata(
        notification_type=NotificationType.RESET_PASSWORD,
        channel=NotificationChannel.EMAIL,
    )

    assert m1.notification_id != m2.notification_id


def test_created_at_auto_populated(notification_metadata):
    assert notification_metadata.created_at is not None


def test_priority_defaults_to_normal():
    meta = NotificationMetadata(
        notification_type=NotificationType.RESET_PASSWORD,
        channel=NotificationChannel.EMAIL,
    )

    assert meta.priority == NotificationPriority.NORMAL


def test_notification_type_required():
    with pytest.raises(Exception):  # noqa: B017
        NotificationMetadata(channel=NotificationChannel.EMAIL)


def test_channel_required():
    with pytest.raises(Exception):  # noqa: B017
        NotificationMetadata(notification_type=NotificationType.RESET_PASSWORD)


@pytest.mark.parametrize(
    "priority,expected",
    [
        (NotificationPriority.LOW, 1),
        (NotificationPriority.NORMAL, 5),
        (NotificationPriority.HIGH, 8),
    ],
)
def test_get_rabbitmq_priority(reset_password_payload, priority, expected):
    message = build_message(
        reset_password_payload,
        NotificationType.RESET_PASSWORD,
        priority=priority,
    )

    assert message.get_rabbitmq_priority() == expected


def test_message_has_metadata_and_payload(reset_password_message):
    assert reset_password_message.metadata is not None
    assert reset_password_message.payload is not None


def test_message_metadata_type_matches(reset_password_message):
    assert (
        reset_password_message.metadata.notification_type
        == NotificationType.RESET_PASSWORD
    )
