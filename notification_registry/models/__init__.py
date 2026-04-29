"""
Модели payload для уведомлений
"""

from notification_registry.models.account_login import AccountLoginPayload
from notification_registry.models.analytics import AnalyticsPayload
from notification_registry.models.base import BaseNotificationPayload
from notification_registry.models.billing_problem import BillingProblemPayload
from notification_registry.models.campaign_status import CampaignStatusPayload
from notification_registry.models.delivery_failed import DeliveryFailedPayload
from notification_registry.models.greeting import GreetingPayload
from notification_registry.models.linkedin import LinkedInDisconnectedPayload
from notification_registry.models.password import ResetPasswordPayload
from notification_registry.models.payment_failed import PaymentFailedPayload
from notification_registry.models.payment_received import PaymentReceivedPayload
from notification_registry.models.subscription_expiring import (
    SubscriptionExpiringPayload,
)

__all__ = [
    "BaseNotificationPayload",
    "AccountLoginPayload",
    "AnalyticsPayload",
    "BillingProblemPayload",
    "CampaignStatusPayload",
    "ResetPasswordPayload",
    "LinkedInDisconnectedPayload",
    "DeliveryFailedPayload",
    "GreetingPayload",
    "PaymentFailedPayload",
    "PaymentReceivedPayload",
    "SubscriptionExpiringPayload",
]
