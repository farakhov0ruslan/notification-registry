from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader

from notification_registry.message import NotificationMessage
from notification_registry.models import AccountLoginPayload
from notification_registry.models import AnalyticsPayload
from notification_registry.models import BillingProblemPayload
from notification_registry.models import CampaignStatusPayload
from notification_registry.models import GreetingPayload
from notification_registry.models import LinkedInDisconnectedPayload
from notification_registry.models import PaymentFailedPayload
from notification_registry.models import PaymentReceivedPayload
from notification_registry.models import ResetPasswordPayload
from notification_registry.models import SubscriptionExpiringPayload
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
        recipient=message.metadata.recipient_address,
        subject=f"Analytics Report: {payload.report_type}",
        body=_render("analytics_report", payload.model_dump(mode="json")),
    )


def process_reset_password_email(
    message: NotificationMessage[ResetPasswordPayload],
) -> ProcessedNotification:
    payload: ResetPasswordPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject="Password Reset Request",
        body=_render("reset_password", payload.model_dump(mode="json")),
    )


def process_linkedin_disconnected_email(
    message: NotificationMessage[LinkedInDisconnectedPayload],
) -> ProcessedNotification:
    payload: LinkedInDisconnectedPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject="LinkedIn Account Disconnected",
        body=_render("linkedin_disconnected", payload.model_dump(mode="json")),
    )


def process_greeting_email(
    message: NotificationMessage[GreetingPayload],
) -> ProcessedNotification:
    payload: GreetingPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject="Welcome to SalesTrigger!",
        body=_render("greeting", payload.model_dump(mode="json")),
    )


def process_account_login_email(
    message: NotificationMessage[AccountLoginPayload],
) -> ProcessedNotification:
    payload: AccountLoginPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject="New login to your SalesTrigger account",
        body=_render("account_login", payload.model_dump(mode="json")),
    )


def process_billing_problem_email(
    message: NotificationMessage[BillingProblemPayload],
) -> ProcessedNotification:
    payload: BillingProblemPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject="Action required: billing issue on your account",
        body=_render("billing_problem", payload.model_dump(mode="json")),
    )


def process_subscription_expiring_email(
    message: NotificationMessage[SubscriptionExpiringPayload],
) -> ProcessedNotification:
    payload: SubscriptionExpiringPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject=f"Your {payload.plan_name} plan expires in {payload.days_until_expiry} days",
        body=_render("subscription_expiring", payload.model_dump(mode="json")),
    )


def process_payment_received_email(
    message: NotificationMessage[PaymentReceivedPayload],
) -> ProcessedNotification:
    payload: PaymentReceivedPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject=f"Payment confirmed: {payload.amount} {payload.currency}",
        body=_render("payment_received", payload.model_dump(mode="json")),
    )


def process_payment_failed_email(
    message: NotificationMessage[PaymentFailedPayload],
) -> ProcessedNotification:
    payload: PaymentFailedPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject="Payment failed — action required",
        body=_render("payment_failed", payload.model_dump(mode="json")),
    )


def process_campaign_status_email(
    message: NotificationMessage[CampaignStatusPayload],
) -> ProcessedNotification:
    payload: CampaignStatusPayload = message.payload
    return ProcessedNotification(
        recipient=message.metadata.recipient_address,
        subject=f"Campaign \"{payload.campaign_name}\": {payload.status}",
        body=_render("campaign_status", payload.model_dump(mode="json")),
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
        NotificationType.GREETING: process_greeting_email,
        NotificationType.ACCOUNT_LOGIN: process_account_login_email,
        NotificationType.BILLING_PROBLEM: process_billing_problem_email,
        NotificationType.SUBSCRIPTION_EXPIRING: process_subscription_expiring_email,
        NotificationType.PAYMENT_RECEIVED: process_payment_received_email,
        NotificationType.PAYMENT_FAILED: process_payment_failed_email,
        NotificationType.CAMPAIGN_STATUS: process_campaign_status_email,
    },
    allow_skip_on_missing=False,
)
