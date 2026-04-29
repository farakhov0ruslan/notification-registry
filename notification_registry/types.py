from enum import StrEnum


class NotificationType(StrEnum):
    # MVP типы
    ANALYTICS = "analytics"
    RESET_PASSWORD = "reset_password"  # noqa: S105
    LINKEDIN_DISCONNECTED = "linkedin_disconnected"

    # Системные типы
    DELIVERY_FAILED = "delivery_failed"

    # Приветственные уведомления
    GREETING = "greeting"

    # Безопасность аккаунта
    ACCOUNT_LOGIN = "account_login"

    # Биллинг и подписки
    BILLING_PROBLEM = "billing_problem"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"

    # Кампании
    CAMPAIGN_STATUS = "campaign_status"
