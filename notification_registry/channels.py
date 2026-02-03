from enum import StrEnum

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
