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

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_jinja_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), autoescape=True)


def _render(template_id: str, data: dict) -> str:
    return _jinja_env.get_template(f"{template_id}.html").render(**data)


def process_analytics_email(
    message: NotificationMessage[AnalyticsPayload],
) -> ProcessedNotification:
    payload: AnalyticsPayload = message.payload
    return ProcessedNotification(
        recipient=payload.recipient_email,
        subject=f"Analytics Report: {payload.report_type}",
        body=_render("analytics_report", payload.model_dump(mode="json")),
    )


def process_reset_password_email(
    message: NotificationMessage[ResetPasswordPayload],
) -> ProcessedNotification:
    payload: ResetPasswordPayload = message.payload
    return ProcessedNotification(
        recipient=payload.recipient_email,
        subject="Password Reset Request",
        body=_render("reset_password", payload.model_dump(mode="json")),
    )


def process_linkedin_disconnected_email(
    message: NotificationMessage[LinkedInDisconnectedPayload],
) -> ProcessedNotification:
    payload: LinkedInDisconnectedPayload = message.payload
    return ProcessedNotification(
        recipient=payload.recipient_email,
        subject="LinkedIn Account Disconnected",
        body=_render("linkedin_disconnected", payload.model_dump(mode="json")),
    )


class _EmailChannelProcessor(BaseChannelProcessor):
    @property
    def channel_name(self) -> str:
        return "email"


EmailChannelProcessor = _EmailChannelProcessor(
    mapper={
        NotificationType.ANALYTICS: process_analytics_email,
        NotificationType.RESET_PASSWORD: process_reset_password_email,
        NotificationType.LINKEDIN_DISCONNECTED: process_linkedin_disconnected_email,
    },
    allow_skip_on_missing=False,
)
