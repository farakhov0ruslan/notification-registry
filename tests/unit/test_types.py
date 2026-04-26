import pytest

from notification_registry import NotificationType


def test_analytics_value_is_stable():
    assert NotificationType.ANALYTICS == "analytics"


def test_reset_password_value_is_stable():
    assert NotificationType.RESET_PASSWORD == "reset_password"


def test_linkedin_disconnected_value_is_stable():
    assert NotificationType.LINKEDIN_DISCONNECTED == "linkedin_disconnected"


def test_delivery_failed_value_is_stable():
    assert NotificationType.DELIVERY_FAILED == "delivery_failed"


def test_notification_type_coercion_from_string():
    assert NotificationType("analytics") == NotificationType.ANALYTICS
    assert NotificationType("reset_password") == NotificationType.RESET_PASSWORD
    assert NotificationType("linkedin_disconnected") == NotificationType.LINKEDIN_DISCONNECTED
    assert NotificationType("delivery_failed") == NotificationType.DELIVERY_FAILED


def test_unknown_notification_type_raises():
    with pytest.raises(ValueError):
        NotificationType("unknown_type")


def test_all_types_are_strings():
    for t in NotificationType:
        assert isinstance(t.value, str)
