from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from notification_registry import AnalyticsPayload
from notification_registry import DeliveryFailedPayload
from notification_registry import LinkedInDisconnectedPayload
from notification_registry import ResetPasswordPayload
from notification_registry.models.base import PhoneNumber

# --- PhoneNumber tests ---


def test_phone_number_valid_format():
    phone = PhoneNumber(number="8-900-123-45-67")

    assert phone.number == "8-900-123-45-67"


def test_phone_number_invalid_plus_format():
    with pytest.raises(ValidationError):
        PhoneNumber(number="+79001234567")


def test_phone_number_invalid_no_dashes():
    with pytest.raises(ValidationError):
        PhoneNumber(number="89001234567")


def test_phone_number_invalid_text():
    with pytest.raises(ValidationError):
        PhoneNumber(number="text")


def test_phone_number_invalid_wrong_format():
    with pytest.raises(ValidationError):
        PhoneNumber(number="8-900-1234-567")


# --- BaseNotificationPayload (via ResetPasswordPayload) ---


@pytest.mark.parametrize(
    "field,value",
    [
        ("recipient_email", "not-an-email"),
        ("recipient_email", "user@.test"),
    ],
)
def test_invalid_email_rejected(reset_password_payload, field, value):
    data = reset_password_payload.model_dump()
    data[field] = value

    with pytest.raises(ValidationError):
        ResetPasswordPayload.model_validate(data)


def test_webhook_url_invalid(reset_password_payload):
    data = reset_password_payload.model_dump()
    data["webhook_url"] = "not a url"

    with pytest.raises(ValidationError):
        ResetPasswordPayload.model_validate(data)


def test_user_id_required():
    with pytest.raises(ValidationError):
        ResetPasswordPayload(
            recipient_email="test@example.com",
            reset_url="https://example.com/reset",
            expires_at=datetime.now(UTC),
            user_name="Test",
            user_ip="127.0.0.1",
            user_agent="test/1.0",
        )


# --- AnalyticsPayload ---


def test_analytics_payload_valid(analytics_payload):
    assert analytics_payload.report_type is not None
    assert analytics_payload.total_leads is not None
    assert analytics_payload.active_campaigns is not None
    assert analytics_payload.engagement_rate is not None


def test_analytics_payload_report_url_optional():
    payload = AnalyticsPayload(
        user_id=uuid4(),
        recipient_email="test@example.com",
        report_type="weekly",
        period_start=datetime.now(UTC) - timedelta(days=7),
        period_end=datetime.now(UTC),
        total_leads=100,
        active_campaigns=5,
        engagement_rate=0.25,
    )

    assert payload.report_url is None


def test_analytics_invalid_total_leads():
    with pytest.raises(ValidationError):
        AnalyticsPayload(
            user_id=uuid4(),
            recipient_email="test@example.com",
            report_type="weekly",
            period_start=datetime.now(UTC) - timedelta(days=7),
            period_end=datetime.now(UTC),
            total_leads="abc",
            active_campaigns=5,
            engagement_rate=0.25,
        )


# --- ResetPasswordPayload ---


def test_reset_password_payload_valid(reset_password_payload):
    assert reset_password_payload.reset_url is not None
    assert reset_password_payload.expires_at is not None
    assert reset_password_payload.user_name is not None


def test_reset_password_invalid_url():
    with pytest.raises(ValidationError):
        ResetPasswordPayload(
            user_id=uuid4(),
            recipient_email="test@example.com",
            reset_url="ftp://invalid",
            expires_at=datetime.now(UTC),
            user_name="Test",
            user_ip="127.0.0.1",
            user_agent="test/1.0",
        )


def test_reset_password_expires_at_parses_iso_string():
    payload = ResetPasswordPayload(
        user_id=uuid4(),
        recipient_email="test@example.com",
        reset_url="https://example.com/reset",
        expires_at="2024-01-26T10:00:00",
        user_name="Test",
        user_ip="127.0.0.1",
        user_agent="test/1.0",
    )

    assert isinstance(payload.expires_at, datetime)


# --- LinkedInDisconnectedPayload ---


def test_linkedin_disconnected_payload_valid(linkedin_disconnected_payload):
    assert linkedin_disconnected_payload.reconnect_url is not None
    assert linkedin_disconnected_payload.reason is not None
    assert linkedin_disconnected_payload.affected_campaigns is not None
    assert linkedin_disconnected_payload.active_sequences is not None


def test_linkedin_reconnect_url_required():
    with pytest.raises(ValidationError):
        LinkedInDisconnectedPayload(
            user_id=uuid4(),
            recipient_email="test@example.com",
            disconnected_at=datetime.now(UTC),
            reason="session_expired",
            affected_campaigns=3,
            active_sequences=2,
        )


def test_linkedin_optional_fields_are_none():
    payload = LinkedInDisconnectedPayload(
        user_id=uuid4(),
        recipient_email="test@example.com",
        disconnected_at=datetime.now(UTC),
        reason="session_expired",
        reconnect_url="https://example.com/reconnect",
        affected_campaigns=3,
        active_sequences=2,
    )

    assert payload.error_message is None
    assert payload.linkedin_profile_url is None


# --- DeliveryFailedPayload ---


def test_delivery_failed_payload_valid(delivery_failed_payload):
    assert delivery_failed_payload.original_channel is not None
    assert delivery_failed_payload.original_type is not None
    assert delivery_failed_payload.error_message is not None
    assert delivery_failed_payload.retry_count is not None
    assert delivery_failed_payload.failed_at is not None


def test_delivery_failed_retry_count_zero():
    payload = DeliveryFailedPayload(
        user_id=uuid4(),
        recipient_email="test@example.com",
        original_channel="email",
        original_type="reset_password",
        error_message="timeout",
        retry_count=0,
        failed_at=datetime.now(UTC),
    )

    assert payload.retry_count == 0


def test_delivery_failed_all_fields_required():
    with pytest.raises(ValidationError):
        DeliveryFailedPayload(
            user_id=uuid4(),
            recipient_email="test@example.com",
            original_channel="email",
        )
