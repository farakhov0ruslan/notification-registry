from notification_registry.models.base import BaseNotificationPayload


class AccountLoginPayload(BaseNotificationPayload):
    """
    Payload уведомления о входе в аккаунт.
    """

    user_name: str
