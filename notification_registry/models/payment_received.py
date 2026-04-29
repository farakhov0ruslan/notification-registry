from typing import Optional

from pydantic import Field

from notification_registry.models.base import BaseNotificationPayload


class PaymentReceivedPayload(BaseNotificationPayload):
    """
    Payload уведомления об успешной оплате.
    """

    user_name: str
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", description="ISO 4217")
    plan_name: str
    receipt_url: Optional[str] = None
