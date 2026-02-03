from notification_registry.message import NotificationMessage
from notification_registry.models import AnalyticsPayload
from notification_registry.models import LinkedInDisconnectedPayload
from notification_registry.models import ResetPasswordPayload
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import ProcessedNotification
from notification_registry.types import NotificationType


def process_analytics_email(message: NotificationMessage[AnalyticsPayload]) -> ProcessedNotification:
    """Обработка аналитического уведомления для email"""
    payload: AnalyticsPayload = message.payload

    return ProcessedNotification()


def process_reset_password_email(message: NotificationMessage[ResetPasswordPayload]) -> ProcessedNotification:
    """Обработка уведомления о сбросе пароля для email"""
    payload = message.payload

    return ProcessedNotification()


def process_linkedin_disconnected_email(
    message: NotificationMessage[LinkedInDisconnectedPayload],
) -> ProcessedNotification:
    """Обработка уведомления об отключении LinkedIn для email"""
    payload = message.payload

    return ProcessedNotification()


class _EmailChannelProcessor(BaseChannelProcessor):
    """Email процессор"""

    @property
    def channel_name(self) -> str:
        return "email"


# Email процессор с маппингом типов уведомлений на функции обработки
EmailChannelProcessor = _EmailChannelProcessor(
    mapper={
        NotificationType.ANALYTICS: process_analytics_email,
        NotificationType.RESET_PASSWORD: process_reset_password_email,
        NotificationType.LINKEDIN_DISCONNECTED: process_linkedin_disconnected_email,
    },
    allow_skip_on_missing=False,
)
