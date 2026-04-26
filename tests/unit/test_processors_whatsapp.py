import json

import pytest

from notification_registry import NotDefinedConvertMethod
from notification_registry import NotificationChannel
from notification_registry import NotificationMessage
from notification_registry import NotificationMetadata
from notification_registry import NotificationPriority
from notification_registry import NotificationType
from notification_registry.models.base import PhoneNumber
from notification_registry.processors.whatsapp import WhatsAppChannelProcessor


def _with_phone(payload):
    return payload.model_copy(
        update={"recipient_phone": PhoneNumber(number="8-999-123-45-67")}
    )


def _message(payload, notification_type):
    return NotificationMessage(
        metadata=NotificationMetadata(
            notification_type=notification_type,
            channel=NotificationChannel.WHATSAPP,
            priority=NotificationPriority.NORMAL,
        ),
        payload=payload,
    )


@pytest.mark.parametrize(
    ("fixture_name", "notification_type", "template_id"),
    [
        ("reset_password_payload", NotificationType.RESET_PASSWORD, "reset_password"),
        ("analytics_payload", NotificationType.ANALYTICS, "analytics"),
        (
            "linkedin_disconnected_payload",
            NotificationType.LINKEDIN_DISCONNECTED,
            "linkedin_disconnected",
        ),
    ],
)
def test_whatsapp_processor_returns_template_payload(
    request,
    fixture_name,
    notification_type,
    template_id,
):
    payload = _with_phone(request.getfixturevalue(fixture_name))
    processed = WhatsAppChannelProcessor.process(_message(payload, notification_type))

    assert processed.recipient == "8-999-123-45-67"
    assert processed.template_id == template_id
    body = json.loads(processed.body)
    assert body["components"]
    assert body["components"][0]["type"] == "body"


def test_whatsapp_processor_raises_for_unsupported_type(delivery_failed_message):
    with pytest.raises(NotDefinedConvertMethod):
        WhatsAppChannelProcessor.process(delivery_failed_message)
