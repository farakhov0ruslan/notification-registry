from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from notification_registry import NotificationChannel
from notification_registry import NotificationMessage
from notification_registry import NotificationMetadata
from notification_registry import NotificationType
from notification_registry import RabbitMQNotificationClient
from notification_registry import deserialize_message


def test_rabbit_client_publish_delegates_to_publisher(
    reset_password_message,
):
    publisher_mock = MagicMock()

    with (
        patch("notification_registry.client.PriorityRabbitPublisher", return_value=publisher_mock),
        RabbitMQNotificationClient() as client,
    ):
        client.publish(reset_password_message)

    publisher_mock.__enter__.assert_called_once()
    publisher_mock.publish.assert_called_once()
    kwargs = publisher_mock.publish.call_args.kwargs
    assert kwargs["queue"] == NotificationChannel.EMAIL.queue_name
    restored = deserialize_message(kwargs["message"].encode())
    assert restored == reset_password_message
    publisher_mock.__exit__.assert_called_once()


def test_rabbit_client_constructor_without_rabbit_config():
    with patch("notification_registry.client.PriorityRabbitPublisher") as rabbit_publisher_cls:
        RabbitMQNotificationClient()

        rabbit_publisher_cls.assert_called_once_with(rabbit_config=None)


def test_rabbit_client_constructor_with_rabbit_config():
    mock_config = MagicMock()

    with patch("notification_registry.client.PriorityRabbitPublisher") as rabbit_publisher_cls:
        RabbitMQNotificationClient(rabbit_config=mock_config)

        rabbit_publisher_cls.assert_called_once_with(rabbit_config=mock_config)


def test_rabbit_client_exit_calls_publisher_exit(
    reset_password_message,
):
    publisher_mock = MagicMock()

    with patch("notification_registry.client.PriorityRabbitPublisher", return_value=publisher_mock):
        client = RabbitMQNotificationClient()
        client.start()
        client.close()

    publisher_mock.__exit__.assert_called_once_with(None, None, None)


def test_rabbit_client_invalid_message_does_not_call_publish(
    analytics_payload,
):
    publisher_mock = MagicMock()

    invalid_message = NotificationMessage(
        metadata=NotificationMetadata(
            notification_type=NotificationType.RESET_PASSWORD,
            channel=NotificationChannel.EMAIL,
        ),
        payload=analytics_payload,
    )

    with (
        patch("notification_registry.client.PriorityRabbitPublisher", return_value=publisher_mock),
        RabbitMQNotificationClient() as client,
        pytest.raises(ValueError),
    ):
        client.publish(invalid_message)

    publisher_mock.publish.assert_not_called()
