from notification_registry.message import NotificationMessage
from notification_registry.models.delivery_failed import DeliveryFailedPayload
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import ProcessedNotification
from notification_registry.types import NotificationType


def process_delivery_failed_platform(
    message: NotificationMessage[DeliveryFailedPayload],
) -> ProcessedNotification:
    """Обработка уведомления о сбое доставки для platform"""
    payload: DeliveryFailedPayload = message.payload

    return ProcessedNotification(
        recipient=str(payload.user_id),
        subject=f"Delivery failed: {payload.original_type} via {payload.original_channel}",
        body=(
            f"Notification delivery failed after {payload.retry_count} attempts. "
            f"Channel: {payload.original_channel}, "
            f"Type: {payload.original_type}. "
            f"Error: {payload.error_message}"
        ),
    )


class _PlatformChannelProcessor(BaseChannelProcessor):
    """Platform процессор"""

    @property
    def channel_name(self) -> str:
        return "platform"


PlatformChannelProcessor = _PlatformChannelProcessor(
    mapper={
        NotificationType.DELIVERY_FAILED: process_delivery_failed_platform,
    },
    allow_skip_on_missing=True,
)
