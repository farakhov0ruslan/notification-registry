import json
from unittest.mock import patch
from uuid import uuid4

import pytest

from notification_registry import NotificationChannel
from notification_registry import NotificationMessage
from notification_registry import NotificationMetadata
from notification_registry import NotificationType
from notification_registry import deserialize_message
from notification_registry import serialize_message
from notification_registry import validate_message
from notification_registry.models.base import BaseNotificationPayload
from notification_registry.serialization import PAYLOAD_TYPE_MAPPING
from tests.conftest import build_message


def test_serialize_returns_bytes(reset_password_message):
    result = serialize_message(reset_password_message)

    assert isinstance(result, bytes)


def test_serialize_has_metadata_and_payload_keys(reset_password_message):
    result = serialize_message(reset_password_message)

    data = json.loads(result)
    assert "metadata" in data
    assert "payload" in data


def test_serialize_notification_id_as_string(reset_password_message):
    result = serialize_message(reset_password_message)

    data = json.loads(result)
    notification_id = data["metadata"]["notification_id"]
    assert isinstance(notification_id, str)


def test_serialize_user_id_as_string(reset_password_message):
    result = serialize_message(reset_password_message)

    data = json.loads(result)
    assert isinstance(data["payload"]["user_id"], str)


def test_serialize_datetime_as_iso(reset_password_message):
    result = serialize_message(reset_password_message)

    data = json.loads(result)
    assert (
        "T" in data["metadata"]["created_at"] or "-" in data["metadata"]["created_at"]
    )


@pytest.mark.parametrize(
    "message_fixture",
    [
        "analytics_message",
        "reset_password_message",
        "linkedin_disconnected_message",
        "delivery_failed_message",
    ],
)
def test_round_trip_preserves_message(message_fixture, request):
    message = request.getfixturevalue(message_fixture)

    restored = deserialize_message(serialize_message(message))

    assert restored == message


def test_deserialize_unknown_notification_type():
    data = {
        "metadata": {
            "notification_id": str(uuid4()),
            "notification_type": "unknown_type_xyz",
            "channel": "email",
            "priority": "normal",
            "created_at": "2024-01-01T00:00:00",
        },
        "payload": {"user_id": str(uuid4())},
    }

    with pytest.raises(ValueError):
        deserialize_message(json.dumps(data).encode())


def test_deserialize_invalid_json():
    with pytest.raises(Exception): # noqa: B017
        deserialize_message(b"not valid json")


def test_deserialize_missing_notification_type():
    data = {
        "metadata": {
            "notification_id": str(uuid4()),
            "channel": "email",
            "priority": "normal",
            "created_at": "2024-01-01T00:00:00",
        },
        "payload": {"user_id": str(uuid4())},
    }

    with pytest.raises((KeyError, ValueError)):
        deserialize_message(json.dumps(data).encode())


# --- validate_message ---


def test_validate_email_channel_with_recipient_address(reset_password_message):
    result = validate_message(reset_password_message)

    assert result is True


def test_validate_email_channel_without_recipient_address(reset_password_payload):
    message = build_message(
        reset_password_payload,
        NotificationType.RESET_PASSWORD,
        channel=NotificationChannel.EMAIL,
        recipient_address=None,
    )

    with pytest.raises(ValueError, match="recipient_address"):
        validate_message(message)


def test_validate_whatsapp_without_recipient_address(reset_password_payload):
    message = build_message(
        reset_password_payload,
        NotificationType.RESET_PASSWORD,
        channel=NotificationChannel.WHATSAPP,
        recipient_address=None,
    )

    with pytest.raises(ValueError, match="recipient_address"):
        validate_message(message)


def test_validate_webhook_without_recipient_address(reset_password_payload):
    message = build_message(
        reset_password_payload,
        NotificationType.RESET_PASSWORD,
        channel=NotificationChannel.WEBHOOK,
        recipient_address=None,
    )

    with pytest.raises(ValueError, match="recipient_address"):
        validate_message(message)


def test_validate_platform_channel_no_requirements(delivery_failed_message):
    result = validate_message(delivery_failed_message)

    assert result is True


def test_validate_payload_type_mismatch(analytics_payload):
    message = NotificationMessage(
        metadata=NotificationMetadata(
            notification_type=NotificationType.RESET_PASSWORD,
            channel=NotificationChannel.EMAIL,
        ),
        payload=analytics_payload,
    )

    with pytest.raises(ValueError, match="mismatch"):
        validate_message(message)


# --- PAYLOAD_TYPE_MAPPING ---


def test_payload_type_mapping_has_all_four_types():
    assert NotificationType.ANALYTICS in PAYLOAD_TYPE_MAPPING
    assert NotificationType.RESET_PASSWORD in PAYLOAD_TYPE_MAPPING
    assert NotificationType.LINKEDIN_DISCONNECTED in PAYLOAD_TYPE_MAPPING
    assert NotificationType.DELIVERY_FAILED in PAYLOAD_TYPE_MAPPING


def test_payload_type_mapping_all_subclass_base():
    for payload_class in PAYLOAD_TYPE_MAPPING.values():
        assert issubclass(payload_class, BaseNotificationPayload)


def test_validate_message_unknown_type_raises(reset_password_payload):
    message = build_message(reset_password_payload, NotificationType.RESET_PASSWORD)

    with (
        patch.object(message.metadata, "notification_type", "completely_unknown_type"),
        pytest.raises((ValueError, KeyError)),
    ):
        validate_message(message)
