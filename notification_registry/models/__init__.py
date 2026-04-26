"""
Модели payload для уведомлений
"""

from notification_registry.models.analytics import AnalyticsPayload
from notification_registry.models.base import BaseNotificationPayload
from notification_registry.models.delivery_failed import DeliveryFailedPayload
from notification_registry.models.linkedin import LinkedInDisconnectedPayload
from notification_registry.models.password import ResetPasswordPayload

__all__ = [
    "BaseNotificationPayload",
    "AnalyticsPayload",
    "ResetPasswordPayload",
    "LinkedInDisconnectedPayload",
    "DeliveryFailedPayload",
]
