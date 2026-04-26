from unittest.mock import Mock
from unittest.mock import patch

from notification_registry import ChannelHandlerSettings
from notification_registry import NotificationChannel
from notification_registry import NotificationType
from notification_registry import build_delivery_failed_callback
from notification_registry import create_channel_consumer
from notification_registry import deserialize_message
from notification_registry import serialize_message


def test_channel_handler_settings_queue_name():
    settings = ChannelHandlerSettings(channel=NotificationChannel.WHATSAPP)

    assert settings.queue_name == NotificationChannel.WHATSAPP.queue_name


def test_create_channel_consumer_forwards_settings():
    settings = ChannelHandlerSettings(
        channel=NotificationChannel.WHATSAPP,
        max_retries=7,
        retry_delay=3.5,
    )
    on_message = Mock()
    publisher = Mock()
    rabbit_config = Mock()

    with patch("notification_registry.channel_handler.NotificationConsumer") as consumer_cls:
        create_channel_consumer(
            settings=settings,
            on_message=on_message,
            publisher=publisher,
            rabbitmq_config=rabbit_config,
        )

    assert consumer_cls.call_args.kwargs["queue_name"] == "notification.whatsapp"
    assert consumer_cls.call_args.kwargs["on_message"] is on_message
    assert consumer_cls.call_args.kwargs["rabbitmq_config"] is rabbit_config
    assert consumer_cls.call_args.kwargs["max_retries"] == 7
    assert consumer_cls.call_args.kwargs["retry_delay"] == 3.5


def test_delivery_failed_callback_publishes_platform_message(reset_password_message):
    publisher = Mock()
    settings = ChannelHandlerSettings(
        channel=NotificationChannel.WHATSAPP,
        max_retries=5,
        failed_error_message="WhatsApp delivery failed after all retries",
    )

    build_delivery_failed_callback(
        publisher=publisher,
        settings=settings,
    )(serialize_message(reset_password_message))

    publisher.publish.assert_called_once()
    assert (
        publisher.publish.call_args.kwargs["queue"]
        == NotificationChannel.PLATFORM.queue_name
    )
    failed = deserialize_message(publisher.publish.call_args.kwargs["message"].encode())
    assert failed.metadata.notification_type == NotificationType.DELIVERY_FAILED
    assert failed.payload.original_channel == "whatsapp"
    assert failed.payload.error_message == "WhatsApp delivery failed after all retries"
