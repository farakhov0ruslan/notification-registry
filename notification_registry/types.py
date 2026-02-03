from enum import StrEnum


class NotificationType(StrEnum):
    # MVP типы
    ANALYTICS = "analytics"
    RESET_PASSWORD = "reset_password"
    LINKEDIN_DISCONNECTED = "linkedin_disconnected"

    # Будущие типы
    # WELCOME = "welcome"
    # LOGIN = "login"
    # BILLING_PROBLEM = "billing_problem"
    # LEAD_UPDATE = "lead_update"
    # CAMPAIGN_STATUS = "campaign_status"
    # REPORT_READY = "report_ready"
    # SUBSCRIPTION_EXPIRING = "subscription_expiring"
    # PAYMENT_RECEIVED = "payment_received"
    # PAYMENT_FAILED = "payment_failed"
    # CUSTOM = "custom"
