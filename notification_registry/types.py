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

    # Будущие типы
    # WELCOME = "welcome" # noqa: ERA001
    # LOGIN = "login" # noqa: ERA001
    # BILLING_PROBLEM = "billing_problem" # noqa: ERA001
    # LEAD_UPDATE = "lead_update" # noqa: ERA001
    # CAMPAIGN_STATUS = "campaign_status" # noqa: ERA001
    # SUBSCRIPTION_EXPIRING = "subscription_expiring" # noqa: ERA001
    # PAYMENT_RECEIVED = "payment_received" # noqa: ERA001
    # PAYMENT_FAILED = "payment_failed" # noqa: ERA001
