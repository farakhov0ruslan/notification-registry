from datetime import datetime

from pydantic import Field
from pydantic import HttpUrl

from notification_registry.models.base import BaseNotificationPayload


class ResetPasswordPayload(BaseNotificationPayload):
    """
    Payload для уведомления о сбросе пароля
    """

    reset_url: HttpUrl = Field(..., description="URL для сброса пароля")
    expires_at: datetime = Field(..., description="Время истечения ссылки")
    user_name: str = Field(..., description="Имя пользователя")
    user_ip: str = Field(..., description="IP-адрес запроса")
    user_agent: str = Field(..., description="User-Agent запроса")
