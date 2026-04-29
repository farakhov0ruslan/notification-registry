from notification_registry.models.base import BaseNotificationPayload


class GreetingPayload(BaseNotificationPayload):
    """
    Payload приветственного уведомления при регистрации пользователя.
    """

    user_name: str
