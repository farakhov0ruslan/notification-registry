import json

from notification_registry.message import NotificationMessage
from notification_registry.models import AnalyticsPayload
from notification_registry.models import LinkedInDisconnectedPayload
from notification_registry.models import ResetPasswordPayload
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import ProcessedNotification
from notification_registry.types import NotificationType


def _text(value: object) -> dict:
    return {
        "type": "text",
        "text": "" if value is None else str(value),
    }


def _body_parameters(*values: object) -> list[dict]:
    return [
        {
            "type": "body",
            "parameters": [_text(value) for value in values],
        }
    ]


def _processed(
    *,
    payload,
    template_id: str,
    components: list[dict],
) -> ProcessedNotification:
    return ProcessedNotification(
        recipient=payload.recipient_phone.number,
        subject=template_id,
        body=json.dumps({"components": components}, default=str),
        template_id=template_id,
        template_data={"components": components},
    )


def process_reset_password_whatsapp(
    message: NotificationMessage[ResetPasswordPayload],
) -> ProcessedNotification:
    payload: ResetPasswordPayload = message.payload
    return _processed(
        payload=payload,
        template_id="reset_password",
        components=_body_parameters(
            payload.user_name,
            payload.reset_url,
            payload.expires_at.isoformat(),
        ),
    )


def process_linkedin_disconnected_whatsapp(
    message: NotificationMessage[LinkedInDisconnectedPayload],
) -> ProcessedNotification:
    payload: LinkedInDisconnectedPayload = message.payload
    return _processed(
        payload=payload,
        template_id="linkedin_disconnected",
        components=_body_parameters(
            payload.linkedin_profile_url or "",
            payload.disconnected_at.isoformat(),
            payload.reason,
            payload.reconnect_url,
            payload.affected_campaigns,
            payload.active_sequences,
        ),
    )


def process_analytics_whatsapp(
    message: NotificationMessage[AnalyticsPayload],
) -> ProcessedNotification:
    payload: AnalyticsPayload = message.payload
    return _processed(
        payload=payload,
        template_id="analytics",
        components=_body_parameters(
            payload.report_type,
            payload.period_start.isoformat(),
            payload.period_end.isoformat(),
            payload.total_leads,
            payload.active_campaigns,
            payload.engagement_rate,
            payload.report_url or "",
        ),
    )


class _WhatsAppChannelProcessor(BaseChannelProcessor):
    """WhatsApp процессор"""

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
