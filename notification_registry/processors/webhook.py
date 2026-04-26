import json

from notification_registry.message import NotificationMessage
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import ProcessedNotification
from notification_registry.types import NotificationType


def _webhook_body(message: NotificationMessage) -> str:
    return json.dumps(
        {
            "notification_type": str(message.metadata.notification_type),
            "notification_id": str(message.metadata.notification_id),
            "created_at": message.metadata.created_at.isoformat(),
            "data": message.payload.model_dump(mode="json"),
        },
        default=str,
    )


def _process_reset_password_webhook(message: NotificationMessage) -> ProcessedNotification:
    return ProcessedNotification(
        recipient=str(message.payload.webhook_url),
        subject=str(message.metadata.notification_type),
        body=_webhook_body(message),
    )


def _process_analytics_webhook(message: NotificationMessage) -> ProcessedNotification:
    return ProcessedNotification(
        recipient=str(message.payload.webhook_url),
        subject=str(message.metadata.notification_type),
        body=_webhook_body(message),
    )


def _process_linkedin_disconnected_webhook(message: NotificationMessage) -> ProcessedNotification:
    return ProcessedNotification(
        recipient=str(message.payload.webhook_url),
        subject=str(message.metadata.notification_type),
        body=_webhook_body(message),
    )


class _WebhookChannelProcessor(BaseChannelProcessor):
    @property
    def channel_name(self) -> str:
        return "webhook"


WebhookChannelProcessor = _WebhookChannelProcessor(
    mapper={
        NotificationType.RESET_PASSWORD: _process_reset_password_webhook,
        NotificationType.ANALYTICS: _process_analytics_webhook,
        NotificationType.LINKEDIN_DISCONNECTED: _process_linkedin_disconnected_webhook,
    },
    allow_skip_on_missing=False,
)
