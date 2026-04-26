from datetime import datetime

from pydantic import Field

from notification_registry.models.base import BaseNotificationPayload


class DeliveryFailedPayload(BaseNotificationPayload):
    """
    Payload для системного уведомления о сбое доставки.

    Публикуется handler-ами при исчерпании retry в очередь notification.platform.
    """

    original_channel: str = Field(
        ..., description="Канал оригинального уведомления (email, webhook, etc.)"
    )
    original_type: str = Field(
        ..., description="Тип оригинального уведомления (notification_type)"
    )
    error_message: str = Field(..., description="Описание ошибки")
    retry_count: int = Field(..., description="Количество выполненных попыток")
    failed_at: datetime = Field(..., description="Время исчерпания попыток")
