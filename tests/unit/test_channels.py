import pytest

from notification_registry import NotificationChannel
from notification_registry import NotificationPriority


@pytest.mark.parametrize(
    "channel,expected",
    [
        (NotificationChannel.EMAIL, "notification.email"),
        (NotificationChannel.PLATFORM, "notification.platform"),
        (NotificationChannel.WEBHOOK, "notification.webhook"),
        (NotificationChannel.WHATSAPP, "notification.whatsapp"),
    ],
)
def test_queue_name_follows_convention(channel, expected):
    assert channel.queue_name == expected


def test_channel_strenum_coercion():
    assert NotificationChannel("email") == NotificationChannel.EMAIL
    assert NotificationChannel("platform") == NotificationChannel.PLATFORM
    assert NotificationChannel("webhook") == NotificationChannel.WEBHOOK
    assert NotificationChannel("whatsapp") == NotificationChannel.WHATSAPP


def test_channel_invalid_value_raises():
    with pytest.raises(ValueError):
        NotificationChannel("sms")


@pytest.mark.parametrize(
    "priority,expected",
    [
        (NotificationPriority.LOW, 1),
        (NotificationPriority.NORMAL, 5),
        (NotificationPriority.HIGH, 8),
    ],
)
def test_rabbitmq_priority_values(priority, expected):
    assert priority.rabbitmq_priority == expected


@pytest.mark.parametrize("priority", list(NotificationPriority))
def test_rabbitmq_priority_in_valid_range(priority):
    assert 0 <= priority.rabbitmq_priority <= 10


def test_priority_strenum_coercion():
    assert NotificationPriority("low") == NotificationPriority.LOW
    assert NotificationPriority("normal") == NotificationPriority.NORMAL
    assert NotificationPriority("high") == NotificationPriority.HIGH
