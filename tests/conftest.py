from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

import pytest
from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from notification_registry import AnalyticsPayload
from notification_registry import DeliveryFailedPayload
from notification_registry import LinkedInDisconnectedPayload
from notification_registry import NotificationChannel
from notification_registry import NotificationMessage
from notification_registry import NotificationMetadata
from notification_registry import NotificationPriority
from notification_registry import NotificationType
from notification_registry import ProcessedNotification
from notification_registry import ResetPasswordPayload


class AnalyticsPayloadFactory(ModelFactory[AnalyticsPayload]):
    recipient_email = Use(lambda: f"user-{uuid4().hex[:8]}@example.com")
    report_type = "weekly"
    report_url = "https://example.com/reports/1"
    period_start = Use(lambda: datetime.now(UTC) - timedelta(days=7))
    period_end = Use(lambda: datetime.now(UTC))
    total_leads = 150
    active_campaigns = 5
    engagement_rate = 0.25
    recipient_phone = None
    webhook_url = None


class ResetPasswordPayloadFactory(ModelFactory[ResetPasswordPayload]):
    recipient_email = Use(lambda: f"user-{uuid4().hex[:8]}@example.com")
    reset_url = "https://example.com/reset?token=abc"
    expires_at = Use(lambda: datetime.now(UTC) + timedelta(hours=1))
    user_name = "Test User"
    user_ip = "127.0.0.1"
    user_agent = "test/1.0"
    recipient_phone = None
    webhook_url = None


class LinkedInDisconnectedPayloadFactory(ModelFactory[LinkedInDisconnectedPayload]):
    recipient_email = Use(lambda: f"user-{uuid4().hex[:8]}@example.com")
    reconnect_url = "https://example.com/linkedin/reconnect"
    disconnected_at = Use(lambda: datetime.now(UTC))
    reason = "session_expired"
    affected_campaigns = 3
    active_sequences = 2
    error_message = None
    linkedin_profile_url = None
    recipient_phone = None
    webhook_url = None


class DeliveryFailedPayloadFactory(ModelFactory[DeliveryFailedPayload]):
    recipient_email = Use(lambda: f"user-{uuid4().hex[:8]}@example.com")
    original_channel = "email"
    original_type = "reset_password"
    error_message = "SMTP timeout"
    retry_count = 5
    failed_at = Use(lambda: datetime.now(UTC))
    recipient_phone = None
    webhook_url = None


class NotificationMetadataFactory(ModelFactory[NotificationMetadata]):
    channel = NotificationChannel.EMAIL
    priority = NotificationPriority.NORMAL
    notification_type = NotificationType.RESET_PASSWORD


class ProcessedNotificationFactory(ModelFactory[ProcessedNotification]):
    recipient = "to@example.com"
    subject = "Subject"
    body = "<html/>"


@pytest.fixture
def analytics_payload():
    return AnalyticsPayloadFactory.build()


@pytest.fixture
def reset_password_payload():
    return ResetPasswordPayloadFactory.build()


@pytest.fixture
def linkedin_disconnected_payload():
    return LinkedInDisconnectedPayloadFactory.build()


@pytest.fixture
def delivery_failed_payload():
    return DeliveryFailedPayloadFactory.build()


@pytest.fixture
def notification_metadata():
    return NotificationMetadataFactory.build()


@pytest.fixture
def processed_notification():
    return ProcessedNotificationFactory.build()


def build_message(
    payload,
    notification_type: NotificationType,
    channel: NotificationChannel = NotificationChannel.EMAIL,
    priority: NotificationPriority = NotificationPriority.NORMAL,
) -> NotificationMessage:
    return NotificationMessage(
        metadata=NotificationMetadata(
            notification_type=notification_type,
            channel=channel,
            priority=priority,
        ),
        payload=payload,
    )


@pytest.fixture
def analytics_message(analytics_payload):
    return build_message(analytics_payload, NotificationType.ANALYTICS)


@pytest.fixture
def reset_password_message(reset_password_payload):
    return build_message(reset_password_payload, NotificationType.RESET_PASSWORD)


@pytest.fixture
def linkedin_disconnected_message(linkedin_disconnected_payload):
    return build_message(
        linkedin_disconnected_payload, NotificationType.LINKEDIN_DISCONNECTED
    )


@pytest.fixture
def delivery_failed_message(delivery_failed_payload):
    return build_message(
        delivery_failed_payload,
        NotificationType.DELIVERY_FAILED,
        channel=NotificationChannel.PLATFORM,
    )
