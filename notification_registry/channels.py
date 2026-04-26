from enum import StrEnum
from typing import Optional


class NotificationChannel(StrEnum):
    """
    Каналы доставки уведомлений
    """

    EMAIL = "email"
    PLATFORM = "platform"
    WEBHOOK = "webhook"
    WHATSAPP = "whatsapp"

    @property
    def queue_name(self) -> str:
        """
        Имя RabbitMQ очереди для канала
        """
        return f"notification.{self.value}"

    @property
    def recipient_field(self) -> Optional[str]:
        """
        Name of the BaseNotificationPayload field this channel requires.
        None means the channel uses user_id implicitly (PLATFORM).
        To add a new channel: add one entry here — no other service logic changes.
        """
        _fields = {
            "email": "recipient_email",
            "webhook": "webhook_url",
            "whatsapp": "recipient_phone",
        }
        return _fields.get(self.value)


class NotificationPriority(StrEnum):
    """
    Приоритет уведомления для обработки
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

    @property
    def rabbitmq_priority(self) -> int:
        """
        Возвращает числовой приоритет для RabbitMQ (0-10)
        """
        mapping = {
            NotificationPriority.LOW: 1,
            NotificationPriority.NORMAL: 5,
            NotificationPriority.HIGH: 8,
        }
        return mapping[self]
