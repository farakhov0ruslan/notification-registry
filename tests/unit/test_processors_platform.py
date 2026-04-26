from notification_registry import NotificationType
from notification_registry import PlatformChannelProcessor
from tests.conftest import build_message


def test_delivery_failed_returns_processed_notification(delivery_failed_payload):
    message = build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=__import__("notification_registry").NotificationChannel.PLATFORM,
    )

    result = PlatformChannelProcessor.process(message)

    assert result is not None


def test_delivery_failed_recipient_is_user_id(delivery_failed_payload):
    from notification_registry import NotificationChannel
    message = build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=NotificationChannel.PLATFORM,
    )

    result = PlatformChannelProcessor.process(message)

    assert result.recipient == str(delivery_failed_payload.user_id)


def test_delivery_failed_template_id(delivery_failed_payload):
    from notification_registry import NotificationChannel
    message = build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=NotificationChannel.PLATFORM,
    )

    result = PlatformChannelProcessor.process(message)

    assert result.template_id == "delivery_failed"


def test_delivery_failed_body_contains_error_message(delivery_failed_payload):
    from notification_registry import NotificationChannel
    message = build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=NotificationChannel.PLATFORM,
    )

    result = PlatformChannelProcessor.process(message)

    assert delivery_failed_payload.error_message in result.body


def test_delivery_failed_body_contains_retry_count(delivery_failed_payload):
    from notification_registry import NotificationChannel
    message = build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=NotificationChannel.PLATFORM,
    )

    result = PlatformChannelProcessor.process(message)

    assert str(delivery_failed_payload.retry_count) in result.body


def test_delivery_failed_subject_contains_channel_and_type(delivery_failed_payload):
    from notification_registry import NotificationChannel
    message = build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=NotificationChannel.PLATFORM,
    )

    result = PlatformChannelProcessor.process(message)

    assert delivery_failed_payload.original_channel in result.subject
    assert delivery_failed_payload.original_type in result.subject


def test_delivery_failed_template_data_has_failed_at_iso(delivery_failed_payload):
    from notification_registry import NotificationChannel
    message = build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=NotificationChannel.PLATFORM,
    )

    result = PlatformChannelProcessor.process(message)

    assert "T" in result.template_data["failed_at"]


def test_other_type_returns_none(reset_password_message):
    result = PlatformChannelProcessor.process(reset_password_message)

    assert result is None


def test_analytics_type_returns_none(analytics_message):
    result = PlatformChannelProcessor.process(analytics_message)

    assert result is None


def test_platform_channel_name():
    assert PlatformChannelProcessor.channel_name == "platform"
