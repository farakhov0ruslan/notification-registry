from pydantic import Field
from pydantic import HttpUrl

from notification_registry.models.base import BaseNotificationPayload


class BillingProblemPayload(BaseNotificationPayload):
    """
    Payload уведомления о проблеме с оплатой/подпиской.
    """

    user_name: str
    issue_type: str = Field(..., description="payment_failed | card_expired | subscription_cancelled")
    billing_url: HttpUrl = Field(..., description="Ссылка на страницу оплаты")
