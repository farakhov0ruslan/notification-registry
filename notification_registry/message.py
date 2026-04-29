from datetime import datetime
from typing import Generic
from typing import Optional
from typing import TypeVar
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field

from notification_registry.channels import NotificationChannel
from notification_registry.channels import NotificationPriority
from notification_registry.types import NotificationType

T = TypeVar("T", bound=BaseModel)


class NotificationMetadata(BaseModel):
    notification_id: UUID = Field(
        default_factory=uuid4, description="Уникальный ID уведомления"
    )
    notification_type: NotificationType = Field(..., description="Тип уведомления")
    channel: NotificationChannel = Field(..., description="Канал доставки")
    priority: NotificationPriority = Field(
        default=NotificationPriority.NORMAL, description="Приоритет обработки"
    )
    recipient_address: Optional[str] = Field(
        None, description="Адрес доставки (email, телефон, URL — зависит от канала)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Время создания"
    )


class NotificationMessage(BaseModel, Generic[T]):
    """
    Общий формат сообщения уведомления для RabbitMQ
    Generic класс, где T - конкретный payload (AnalyticsPayload, ResetPasswordPayload, etc.)
    """

    metadata: NotificationMetadata = Field(..., description="Метаданные уведомления")
    payload: T = Field(..., description="Данные уведомления")

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "notification_id": "123e4567-e89b-12d3-a456-426614174000",
                    "notification_type": "analytics",
                    "channel": "email",
                    "priority": "normal",
                    "created_at": "2024-01-26T10:00:00Z",
                },
                "payload": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "recipient_email": "user@example.com",
                    "report_type": "weekly",
                    "total_leads": 150,
                },
            }
        }

    def get_rabbitmq_priority(self) -> int:
        """
        Возвращает числовой приоритет для RabbitMQ
        """
        return self.metadata.priority.rabbitmq_priority
