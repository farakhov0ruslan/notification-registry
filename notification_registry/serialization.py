import json
from typing import Type
from typing import TypeVar

from notification_registry.channels import NotificationChannel
from notification_registry.message import NotificationMessage
from notification_registry.models import AccountLoginPayload
from notification_registry.models import AnalyticsPayload
from notification_registry.models import BaseNotificationPayload
from notification_registry.models import BillingProblemPayload
from notification_registry.models import CampaignStatusPayload
from notification_registry.models import DeliveryFailedPayload
from notification_registry.models import GreetingPayload
from notification_registry.models import LinkedInDisconnectedPayload
from notification_registry.models import PaymentFailedPayload
from notification_registry.models import PaymentReceivedPayload
from notification_registry.models import ResetPasswordPayload
from notification_registry.models import SubscriptionExpiringPayload
from notification_registry.types import NotificationType

T = TypeVar("T", bound=BaseNotificationPayload)


# Маппинг типов уведомлений на классы payload
PAYLOAD_TYPE_MAPPING: dict[NotificationType, Type[BaseNotificationPayload]] = {
    NotificationType.ANALYTICS: AnalyticsPayload,
    NotificationType.RESET_PASSWORD: ResetPasswordPayload,
    NotificationType.LINKEDIN_DISCONNECTED: LinkedInDisconnectedPayload,
    NotificationType.DELIVERY_FAILED: DeliveryFailedPayload,
    NotificationType.GREETING: GreetingPayload,
    NotificationType.ACCOUNT_LOGIN: AccountLoginPayload,
    NotificationType.BILLING_PROBLEM: BillingProblemPayload,
    NotificationType.CAMPAIGN_STATUS: CampaignStatusPayload,
    NotificationType.SUBSCRIPTION_EXPIRING: SubscriptionExpiringPayload,
    NotificationType.PAYMENT_RECEIVED: PaymentReceivedPayload,
    NotificationType.PAYMENT_FAILED: PaymentFailedPayload,
}


def serialize_message(message: NotificationMessage) -> bytes:
    """
    Сериализует NotificationMessage в bytes для отправки в RabbitMQ
    """
    json_str = message.model_dump_json()
    return json_str.encode("utf-8")


def deserialize_message(data: bytes) -> NotificationMessage:
    """
    Десериализует bytes в NotificationMessage
    """
    # Декодируем JSON
    json_str = data.decode("utf-8")
    raw_dict = json.loads(json_str)

    # Получаем тип уведомления из метаданных
    notification_type = NotificationType(raw_dict["metadata"]["notification_type"])

    # Находим соответствующий класс payload
    payload_class = PAYLOAD_TYPE_MAPPING.get(notification_type)
    if payload_class is None:  # pragma: no cover
        raise ValueError(
            f"Unknown notification type: {notification_type}. "
            f"Available types: {list(PAYLOAD_TYPE_MAPPING.keys())}"
        )

    # Парсим payload с правильным классом
    payload = payload_class.model_validate(raw_dict["payload"])

    # Создаем NotificationMessage
    # Используем model_validate для metadata чтобы правильно обработать все поля
    from notification_registry.message import NotificationMetadata

    metadata = NotificationMetadata.model_validate(raw_dict["metadata"])

    return NotificationMessage(metadata=metadata, payload=payload)


def validate_message(message: NotificationMessage) -> bool:
    # Проверяем что тип payload соответствует notification_type
    expected_class = PAYLOAD_TYPE_MAPPING.get(message.metadata.notification_type)
    if expected_class is None:
        raise ValueError(
            f"Unknown notification type: {message.metadata.notification_type}"
        )

    if not isinstance(message.payload, expected_class):
        raise ValueError(
            f"Payload type mismatch: expected {expected_class.__name__}, "
            f"got {type(message.payload).__name__}"
        )

    # Проверяем наличие recipient_address для не-платформенных каналов
    if (
        message.metadata.channel != NotificationChannel.PLATFORM
        and not message.metadata.recipient_address
    ):
        raise ValueError(
            f"recipient_address is required for {message.metadata.channel.value} channel"
        )

    return True
