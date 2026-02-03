from pydantic import Field

from notification_registry.models.base import BaseNotificationPayload


class AnalyticsPayload(BaseNotificationPayload):
    """
    Payload для отчетов и статистики
    """
    # TODO: implement fields
    info: dict = Field(..., description="info")
