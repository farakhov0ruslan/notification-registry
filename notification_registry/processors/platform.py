import json

from notification_registry.message import NotificationMessage
from notification_registry.models.account_login import AccountLoginPayload
from notification_registry.models.analytics import AnalyticsPayload
from notification_registry.models.billing_problem import BillingProblemPayload
from notification_registry.models.campaign_status import CampaignStatusPayload
from notification_registry.models.delivery_failed import DeliveryFailedPayload
from notification_registry.models.greeting import GreetingPayload
from notification_registry.models.linkedin import LinkedInDisconnectedPayload
from notification_registry.models.password import ResetPasswordPayload
from notification_registry.models.payment_failed import PaymentFailedPayload
from notification_registry.models.payment_received import PaymentReceivedPayload
from notification_registry.models.subscription_expiring import SubscriptionExpiringPayload
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import ProcessedNotification
from notification_registry.types import NotificationType


def _process_account_login(message: NotificationMessage[AccountLoginPayload]) -> ProcessedNotification:
    payload: AccountLoginPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=f"New sign-in to your account from {payload.user_name}.",
    )


def _process_greeting(message: NotificationMessage[GreetingPayload]) -> ProcessedNotification:
    payload: GreetingPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=f"Welcome to SalesTrigger, {payload.user_name}!",
    )


def _process_reset_password(message: NotificationMessage[ResetPasswordPayload]) -> ProcessedNotification:
    payload: ResetPasswordPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=(
            f"Password reset requested from IP {payload.user_ip}. "
            f"Link expires at {payload.expires_at.strftime('%Y-%m-%d %H:%M')} UTC."
        ),
    )


def _process_analytics(message: NotificationMessage[AnalyticsPayload]) -> ProcessedNotification:
    payload: AnalyticsPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=(
            f"{payload.report_type.capitalize()} report: {payload.total_leads} leads, "
            f"{payload.active_campaigns} campaigns, {payload.engagement_rate:.0%} engagement."
        ),
    )


def _process_linkedin_disconnected(message: NotificationMessage[LinkedInDisconnectedPayload]) -> ProcessedNotification:
    payload: LinkedInDisconnectedPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=(
            f"LinkedIn account disconnected. "
            f"{payload.affected_campaigns} campaigns and {payload.active_sequences} sequences affected."
        ),
    )


def _process_billing_problem(message: NotificationMessage[BillingProblemPayload]) -> ProcessedNotification:
    payload: BillingProblemPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=f"Billing issue: {payload.issue_type}. Please update your payment details.",
    )


def _process_subscription_expiring(message: NotificationMessage[SubscriptionExpiringPayload]) -> ProcessedNotification:
    payload: SubscriptionExpiringPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=(
            f"Your {payload.plan_name} plan expires in {payload.days_until_expiry} day(s) "
            f"({payload.expires_at.strftime('%Y-%m-%d')})."
        ),
    )


def _process_payment_received(message: NotificationMessage[PaymentReceivedPayload]) -> ProcessedNotification:
    payload: PaymentReceivedPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=f"Payment of {payload.amount} {payload.currency} for {payload.plan_name} plan received.",
    )


def _process_payment_failed(message: NotificationMessage[PaymentFailedPayload]) -> ProcessedNotification:
    payload: PaymentFailedPayload = message.payload
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=f"Payment of {payload.amount} {payload.currency} failed: {payload.reason}.",
    )


def _process_campaign_status(message: NotificationMessage[CampaignStatusPayload]) -> ProcessedNotification:
    payload: CampaignStatusPayload = message.payload
    leads_part = f" Leads processed: {payload.leads_processed}." if payload.leads_processed is not None else ""
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=f"Campaign \"{payload.campaign_name}\": {payload.status}.{leads_part}",
    )


def _format_delivery_error(error: str) -> str:
    # Keep only the first meaningful line, strip raw JSON/URLs from the end.
    # Typical format: "Webhook delivery failed to https://...: 404: {...}"
    # We want: "HTTP 404" or just the first sentence.
    import re
    match = re.search(r":\s*(\d{3})\b", error)
    if match:
        return f"HTTP {match.group(1)}"
    # Fallback: first 120 chars, no newlines
    return error.split("\n")[0][:120]


def process_delivery_failed_platform(
    message: NotificationMessage[DeliveryFailedPayload],
) -> ProcessedNotification:
    payload: DeliveryFailedPayload = message.payload
    attempts = payload.retry_count
    attempt_word = "attempt" if attempts == 1 else "attempts"
    channel = payload.original_channel.capitalize()
    notification_type = payload.original_type.replace("_", " ").title()
    reason = _format_delivery_error(payload.error_message)
    return ProcessedNotification(
        recipient=str(payload.user_id),
        body=(
            f"{notification_type} could not be delivered via {channel} "
            f"after {attempts} {attempt_word}.\n"
            f"Reason: {reason}"
        ),
    )


def process_generic_platform(message: NotificationMessage) -> ProcessedNotification:
    return ProcessedNotification(
        recipient=str(message.payload.user_id),
        body=json.dumps(message.payload.model_dump(mode="json"), default=str),
    )


class _PlatformChannelProcessor(BaseChannelProcessor):
    @property
    def channel_name(self) -> str:
        return "platform"


PlatformChannelProcessor = _PlatformChannelProcessor(
    mapper={
        NotificationType.ACCOUNT_LOGIN: _process_account_login,
        NotificationType.GREETING: _process_greeting,
        NotificationType.RESET_PASSWORD: _process_reset_password,
        NotificationType.ANALYTICS: _process_analytics,
        NotificationType.LINKEDIN_DISCONNECTED: _process_linkedin_disconnected,
        NotificationType.BILLING_PROBLEM: _process_billing_problem,
        NotificationType.SUBSCRIPTION_EXPIRING: _process_subscription_expiring,
        NotificationType.PAYMENT_RECEIVED: _process_payment_received,
        NotificationType.PAYMENT_FAILED: _process_payment_failed,
        NotificationType.CAMPAIGN_STATUS: _process_campaign_status,
        NotificationType.DELIVERY_FAILED: process_delivery_failed_platform,
    },
    default_handler=process_generic_platform,
)
