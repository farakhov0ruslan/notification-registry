import pytest

from notification_registry import deserialize_message
from notification_registry import serialize_message


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

    body = serialize_message(message)
    restored = deserialize_message(body)

    assert restored == message


def test_round_trip_reset_password_payload_fields(reset_password_message):
    body = serialize_message(reset_password_message)

    restored = deserialize_message(body)

    assert restored.payload.user_name == reset_password_message.payload.user_name
    assert restored.payload.user_ip == reset_password_message.payload.user_ip
    assert restored.payload.user_agent == reset_password_message.payload.user_agent


def test_round_trip_analytics_payload_fields(analytics_message):
    body = serialize_message(analytics_message)

    restored = deserialize_message(body)

    assert restored.payload.report_type == analytics_message.payload.report_type
    assert restored.payload.total_leads == analytics_message.payload.total_leads
    assert restored.payload.active_campaigns == analytics_message.payload.active_campaigns


def test_round_trip_delivery_failed_payload_fields(delivery_failed_message):
    body = serialize_message(delivery_failed_message)

    restored = deserialize_message(body)

    assert restored.payload.original_channel == delivery_failed_message.payload.original_channel
    assert restored.payload.error_message == delivery_failed_message.payload.error_message
    assert restored.payload.retry_count == delivery_failed_message.payload.retry_count


def test_round_trip_metadata_preserved(reset_password_message):
    body = serialize_message(reset_password_message)

    restored = deserialize_message(body)

    assert restored.metadata.notification_id == reset_password_message.metadata.notification_id
    assert restored.metadata.notification_type == reset_password_message.metadata.notification_type
    assert restored.metadata.channel == reset_password_message.metadata.channel
    assert restored.metadata.priority == reset_password_message.metadata.priority
