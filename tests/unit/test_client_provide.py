from unittest.mock import patch

from notification_registry import LocalNotificationClient
from notification_registry import RabbitMQNotificationClient
from notification_registry import provide_notification_client


def test_main_environment_returns_rabbit_client():
    with patch("notification_registry.client.RabbitPublisher"):
        client = provide_notification_client("main")

    assert isinstance(client, RabbitMQNotificationClient)


def test_local_environment_returns_local_client():
    client = provide_notification_client("local")

    assert isinstance(client, LocalNotificationClient)


def test_dev_environment_returns_local_client():
    client = provide_notification_client("dev")

    assert isinstance(client, LocalNotificationClient)


def test_test_environment_returns_local_client():
    client = provide_notification_client("test")

    assert isinstance(client, LocalNotificationClient)


def test_empty_string_environment_returns_local_client():
    client = provide_notification_client("")

    assert isinstance(client, LocalNotificationClient)


def test_handler_passed_to_local_client():
    def my_handler(queue_name, body):
        pass

    client = provide_notification_client("local", handler=my_handler)

    assert client.handler is my_handler


def test_handler_passed_for_dev_environment():
    received = []

    def handler(queue_name, body):
        received.append(queue_name)

    client = provide_notification_client("dev", handler=handler)

    assert isinstance(client, LocalNotificationClient)
    assert client.handler is handler
