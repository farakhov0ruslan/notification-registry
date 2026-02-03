from datetime import datetime
from typing import Optional

from pydantic import Field
from pydantic import HttpUrl

from notification_registry.models.base import BaseNotificationPayload


class LinkedInDisconnectedPayload(BaseNotificationPayload):
    """
    Payload для уведомления об отключении LinkedIn аккаунта
    """

    linkedin_profile_url: Optional[str] = Field(
        None, description="URL профиля LinkedIn"
    )
    disconnected_at: datetime = Field(..., description="Время отключения")

    reason: str = Field(
        ...,
        description="Причина отключения (session_expired, revoked, api_error)",
    )
    error_message: Optional[str] = Field(
        None, description="Сообщение об ошибке если есть"
    )