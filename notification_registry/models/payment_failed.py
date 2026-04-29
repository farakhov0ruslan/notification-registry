from pydantic import Field
from pydantic import HttpUrl

from notification_registry.models.base import BaseNotificationPayload


class PaymentFailedPayload(BaseNotificationPayload):
    """
    Payload уведомления о неудачной оплате.
    """

    user_name: str
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", description="ISO 4217")
    reason: str = Field(..., description="card_declined | insufficient_funds | card_expired")
    retry_url: HttpUrl
