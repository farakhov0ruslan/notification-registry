import pytest

from notification_registry import LocalNotificationClient
from notification_registry import NotificationChannel
from notification_registry import NotificationType
from notification_registry import deserialize_message
from notification_registry import serialize_message
from notification_registry.serialization import validate_message
from tests.conftest import AnalyticsPayloadFactory
from tests.conftest import build_message


def test_publish_stores_queue_name_and_body(reset_password_message):
    client = LocalNotificationClient()

    client.start()
    client.publish(reset_password_message)
    client.close()

    assert len(client.published) == 1
    queue_name, body = client.published[0]
    assert queue_name == NotificationChannel.EMAIL.queue_name


def test_publish_body_is_deserializable(reset_password_message):
    client = LocalNotificationClient()

    client.start()
    client.publish(reset_password_message)
    client.close()

    _, body = client.published[0]
    restored = deserialize_message(body)
    assert restored == reset_password_message


def test_publish_calls_handler_with_queue_and_body(reset_password_message):
    received = []

    def handler(queue_name, body):
        received.append((queue_name, body))

    with LocalNotificationClient(handler=handler) as client:
        client.publish(reset_password_message)

    assert len(received) == 1
    assert received[0][0] == NotificationChannel.EMAIL.queue_name
    assert deserialize_message(received[0][1]) == reset_password_message


def test_no_handler_no_error(reset_password_message):
    with LocalNotificationClient() as client:
        client.publish(reset_password_message)

    assert len(client.published) == 1


def test_handler_raises_propagates(reset_password_message):
    def bad_handler(queue_name, body):
        raise RuntimeError("handler failure")

    client = LocalNotificationClient(handler=bad_handler)
    client.start()

    with pytest.raises(RuntimeError, match="handler failure"):
        client.publish(reset_password_message)


def test_invalid_message_payload_mismatch_raises_before_publish(analytics_payload):
    from notification_registry import NotificationMessage
    from notification_registry import NotificationMetadata
    message = NotificationMessage(
        metadata=NotificationMetadata(
            notification_type=NotificationType.RESET_PASSWORD,
            channel=NotificationChannel.EMAIL,
        ),
        payload=analytics_payload,
    )
    client = LocalNotificationClient()
    client.start()

    with pytest.raises(ValueError):
        client.publish(message)

    assert len(client.published) == 0


def test_multiple_publishes_order_preserved(
    reset_password_message, analytics_message, linkedin_disconnected_message
):
    client = LocalNotificationClient()
    client.start()
    client.publish(reset_password_message)
    client.publish(analytics_message)
    client.publish(linkedin_disconnected_message)
    client.close()

    assert len(client.published) == 3
    assert client.published[0][0] == NotificationChannel.EMAIL.queue_name
    assert client.published[1][0] == NotificationChannel.EMAIL.queue_name
    assert client.published[2][0] == NotificationChannel.EMAIL.queue_name


def test_context_manager_calls_start_and_close():
    logs = []

    with LocalNotificationClient(logger=logs.append) as client:
        pass

    assert any("started" in log.lower() for log in logs)
    assert any("closed" in log.lower() for log in logs)


def test_start_without_context_manager(reset_password_message):
    client = LocalNotificationClient()

    client.start()
    client.publish(reset_password_message)
    client.close()

    assert len(client.published) == 1
