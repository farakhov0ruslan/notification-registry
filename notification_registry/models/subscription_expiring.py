from datetime import datetime

from pydantic import Field
from pydantic import HttpUrl

from notification_registry.models.base import BaseNotificationPayload


class SubscriptionExpiringPayload(BaseNotificationPayload):
    """
    Payload уведомления об истекающей подписке.
    """

    user_name: str
    plan_name: str
    expires_at: datetime
    days_until_expiry: int = Field(..., ge=0)
    renewal_url: HttpUrl
