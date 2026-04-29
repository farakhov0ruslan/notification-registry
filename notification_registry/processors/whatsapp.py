from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader

from notification_registry.message import NotificationMessage
from notification_registry.models import AnalyticsPayload
from notification_registry.models import LinkedInDisconnectedPayload
from notification_registry.models import ResetPasswordPayload
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import ProcessedNotification
from notification_registry.types import NotificationType

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "whatsapp"
_jinja_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), autoescape=False)


def _render(template_id: str, data: dict) -> str:
    return _jinja_env.get_template(f"{template_id}.json.j2").render(**data)


def process_reset_password_whatsapp(
    message: NotificationMessage[ResetPasswordPayload],
) -> ProcessedNotification:
    payload: ResetPasswordPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        body=_render("reset_password", payload.model_dump(mode="json")),
    )


def process_linkedin_disconnected_whatsapp(
    message: NotificationMessage[LinkedInDisconnectedPayload],
) -> ProcessedNotification:
    payload: LinkedInDisconnectedPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        body=_render("linkedin_disconnected", payload.model_dump(mode="json")),
    )


def process_analytics_whatsapp(
    message: NotificationMessage[AnalyticsPayload],
) -> ProcessedNotification:
    payload: AnalyticsPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        body=_render("analytics", payload.model_dump(mode="json")),
    )


class _WhatsAppChannelProcessor(BaseChannelProcessor):
    @property
    def channel_name(self) -> str:
        return "whatsapp"


WhatsAppChannelProcessor = _WhatsAppChannelProcessor(
    mapper={
        NotificationType.RESET_PASSWORD: process_reset_password_whatsapp,
        NotificationType.LINKEDIN_DISCONNECTED: process_linkedin_disconnected_whatsapp,
        NotificationType.ANALYTICS: process_analytics_whatsapp,
    },
    allow_skip_on_missing=False,
)
