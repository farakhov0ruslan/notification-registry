import pytest

from notification_registry import EmailChannelProcessor
from notification_registry import NotificationType
from notification_registry.processors.base import NotDefinedConvertMethod
from tests.conftest import AnalyticsPayloadFactory
from tests.conftest import LinkedInDisconnectedPayloadFactory
from tests.conftest import ResetPasswordPayloadFactory
from tests.conftest import build_message


def test_reset_password_renders_correct_recipient(reset_password_payload):
    message = build_message(reset_password_payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert result.recipient == message.metadata.recipient_address


def test_reset_password_renders_subject(reset_password_payload):
    message = build_message(reset_password_payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert result.subject == "Password Reset Request"


def test_reset_password_renders_doctype(reset_password_payload):
    message = build_message(reset_password_payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert "<!DOCTYPE html>" in result.body


def test_reset_password_renders_user_name(reset_password_payload):
    payload = reset_password_payload.model_copy(update={"user_name": "Alice"})
    message = build_message(payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert "Alice" in result.body


def test_reset_password_renders_reset_url(reset_password_payload):
    message = build_message(reset_password_payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert str(reset_password_payload.reset_url) in result.body


def test_reset_password_renders_salestrigger_footer(reset_password_payload):
    message = build_message(reset_password_payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert "SalesTrigger" in result.body


def test_reset_password_no_user_name_renders_hello(reset_password_payload):
    payload = reset_password_payload.model_copy(update={"user_name": ""})
    message = build_message(payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert "Hello," in result.body


def test_html_is_escaped_in_user_fields():
    payload = ResetPasswordPayloadFactory.build(user_name="<script>alert(1)</script>")
    message = build_message(payload, NotificationType.RESET_PASSWORD)

    result = EmailChannelProcessor.process(message)

    assert "<script>" not in result.body
    assert "&lt;script&gt;" in result.body


# --- Analytics ---


def test_analytics_renders_correct_recipient(analytics_payload):
    message = build_message(analytics_payload, NotificationType.ANALYTICS)

    result = EmailChannelProcessor.process(message)

    assert result.recipient == message.metadata.recipient_address


def test_analytics_renders_subject(analytics_payload):
    message = build_message(analytics_payload, NotificationType.ANALYTICS)

    result = EmailChannelProcessor.process(message)

    assert analytics_payload.report_type in result.subject


def test_analytics_renders_doctype(analytics_payload):
    message = build_message(analytics_payload, NotificationType.ANALYTICS)

    result = EmailChannelProcessor.process(message)

    assert "<!DOCTYPE html>" in result.body


def test_analytics_renders_total_leads(analytics_payload):
    message = build_message(analytics_payload, NotificationType.ANALYTICS)

    result = EmailChannelProcessor.process(message)

    assert str(analytics_payload.total_leads) in result.body


def test_analytics_with_report_url_renders_link(analytics_payload):
    payload = analytics_payload.model_copy(
        update={"report_url": "https://example.com/report/123"}
    )
    message = build_message(payload, NotificationType.ANALYTICS)

    result = EmailChannelProcessor.process(message)

    assert "View Full Report" in result.body


def test_analytics_without_report_url_no_button():
    payload = AnalyticsPayloadFactory.build(report_url=None)
    message = build_message(payload, NotificationType.ANALYTICS)

    result = EmailChannelProcessor.process(message)

    assert "View Full Report" not in result.body


# --- LinkedIn Disconnected ---


def test_linkedin_disconnected_renders_correct_recipient(linkedin_disconnected_payload):
    message = build_message(
        linkedin_disconnected_payload, NotificationType.LINKEDIN_DISCONNECTED
    )

    result = EmailChannelProcessor.process(message)

    assert result.recipient == message.metadata.recipient_address


def test_linkedin_disconnected_renders_subject(linkedin_disconnected_payload):
    message = build_message(
        linkedin_disconnected_payload, NotificationType.LINKEDIN_DISCONNECTED
    )

    result = EmailChannelProcessor.process(message)

    assert result.subject == "LinkedIn Account Disconnected"


def test_linkedin_disconnected_renders_doctype(linkedin_disconnected_payload):
    message = build_message(
        linkedin_disconnected_payload, NotificationType.LINKEDIN_DISCONNECTED
    )

    result = EmailChannelProcessor.process(message)

    assert "<!DOCTYPE html>" in result.body


def test_linkedin_disconnected_renders_reason(linkedin_disconnected_payload):
    message = build_message(
        linkedin_disconnected_payload, NotificationType.LINKEDIN_DISCONNECTED
    )

    result = EmailChannelProcessor.process(message)

    assert linkedin_disconnected_payload.reason in result.body


def test_linkedin_disconnected_without_error_message_no_details_row():
    payload = LinkedInDisconnectedPayloadFactory.build(error_message=None)
    message = build_message(payload, NotificationType.LINKEDIN_DISCONNECTED)

    result = EmailChannelProcessor.process(message)

    assert "Details" not in result.body


def test_linkedin_disconnected_with_error_message_renders_details():
    payload = LinkedInDisconnectedPayloadFactory.build(
        error_message="Token revoked by user"
    )
    message = build_message(payload, NotificationType.LINKEDIN_DISCONNECTED)

    result = EmailChannelProcessor.process(message)

    assert "Details" in result.body
    assert "Token revoked by user" in result.body


def test_linkedin_disconnected_with_affected_campaigns_renders_count():
    payload = LinkedInDisconnectedPayloadFactory.build(affected_campaigns=3)
    message = build_message(payload, NotificationType.LINKEDIN_DISCONNECTED)

    result = EmailChannelProcessor.process(message)

    assert "3" in result.body


def test_linkedin_disconnected_with_zero_campaigns_no_iteration_error():
    payload = LinkedInDisconnectedPayloadFactory.build(affected_campaigns=0)
    message = build_message(payload, NotificationType.LINKEDIN_DISCONNECTED)

    result = EmailChannelProcessor.process(message)

    assert result.body is not None


# --- Unsupported type ---


def test_delivery_failed_type_raises_not_defined_convert_method(
    delivery_failed_message,
):
    with pytest.raises(NotDefinedConvertMethod):
        EmailChannelProcessor.process(delivery_failed_message)
