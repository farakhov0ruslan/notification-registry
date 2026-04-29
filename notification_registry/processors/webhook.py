import json

from notification_registry.message import NotificationMessage
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import ProcessedNotification


def _process_generic_webhook(message: NotificationMessage) -> ProcessedNotification:
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject=str(message.metadata.notification_type),
        body=json.dumps(
            {
                "notification_type": str(message.metadata.notification_type),
                "notification_id": str(message.metadata.notification_id),
                "created_at": message.metadata.created_at.isoformat(),
                "data": message.payload.model_dump(mode="json"),
            },
            default=str,
        ),
    )


class _WebhookChannelProcessor(BaseChannelProcessor):
    @property
    def channel_name(self) -> str:
        return "webhook"


WebhookChannelProcessor = _WebhookChannelProcessor(
    mapper={},
    default_handler=_process_generic_webhook,
    allow_skip_on_missing=False,
)
