from datetime import datetime

from pydantic import Field
from pydantic import HttpUrl

from notification_registry.models.base import BaseNotificationPayload


class ResetPasswordPayload(BaseNotificationPayload):
    """
    Payload для уведомления о сбросе пароля
    """

    # TODO: implement fields
    info: dict = Field(..., description="info")