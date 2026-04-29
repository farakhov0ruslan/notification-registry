from abc import ABC
from abc import abstractmethod
from typing import Callable

from pydantic import BaseModel

from notification_registry.message import NotificationMessage
from notification_registry.types import NotificationType


class NotDefinedConvertMethod(Exception):
    """Исключение когда метод конвертации для типа уведомления не определен"""

    def __init__(self, notification_type: NotificationType, channel: str):
        self.notification_type = notification_type
        self.channel = channel
        super().__init__(
            f"Convert method for notification type '{notification_type}' "
            f"is not defined in {channel} processor"
        )


class ProcessedNotification(BaseModel):
    recipient: str  # email, phone, webhook_url, user_id - зависит от канала
    subject: str | None = None  # тема письма для email
    body: str  # HTML/text для email, JSON для webhook/whatsapp, text для platform


class BaseChannelProcessor(ABC):
    """
    Базовый процессор для конвертации NotificationMessage в формат канала

    Каждый канал (Email, Platform, Webhook, WhatsApp) должен реализовать
    свой процессор наследуясь от этого класса.
    """

    def __init__(
        self,
        mapper: dict[
            NotificationType, Callable[[NotificationMessage], ProcessedNotification]
        ],
        allow_skip_on_missing: bool = False,
        default_handler: Callable[[NotificationMessage], ProcessedNotification] | None = None,
    ):
        """
        Args:
            mapper: словарь {тип_уведомления: функция_обработки}
            allow_skip_on_missing: если True, пропускать уведомления без обработчика
            default_handler: обработчик для типов, отсутствующих в mapper
        """
        self.mapper = mapper
        self.allow_skip_on_missing = allow_skip_on_missing
        self.default_handler = default_handler

    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Имя канала для логирования"""

    def process(self, message: NotificationMessage) -> ProcessedNotification | None:
        """
        Обрабатывает NotificationMessage и конвертирует в ProcessedNotification
        """
        notification_type = message.metadata.notification_type

        if notification_type not in self.mapper:
            if self.default_handler is not None:
                return self.default_handler(message)
            if self.allow_skip_on_missing:
                return None
            raise NotDefinedConvertMethod(notification_type, self.channel_name)

        # Вызываем соответствующую функцию обработки
        convert_fn = self.mapper[notification_type]
        return convert_fn(message)

    def can_process(self, notification_type: NotificationType) -> bool:
        """
        Проверяет может ли процессор обработать данный тип уведомления
        """
        return notification_type in self.mapper

    def supported_types(self) -> list[NotificationType]:
        """
        Возвращает список поддерживаемых типов уведомлений
        """
        return list(self.mapper.keys())
