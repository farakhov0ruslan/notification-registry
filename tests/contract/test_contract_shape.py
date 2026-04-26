import json

import pytest

from notification_registry import serialize_message


METADATA_KEYS = {"notification_id", "notification_type", "channel", "priority", "created_at"}


def test_reset_password_wire_format(reset_password_message):
    body = serialize_message(reset_password_message)
    data = json.loads(body)

    assert set(data.keys()) == {"metadata", "payload"}
    assert set(data["metadata"].keys()) == METADATA_KEYS
    required_payload_fields = {
        "user_id", "recipient_email", "reset_url", "expires_at",
        "user_name", "user_ip", "user_agent",
    }
    assert required_payload_fields <= set(data["payload"].keys())


def test_analytics_wire_format(analytics_message):
    body = serialize_message(analytics_message)
    data = json.loads(body)

    assert set(data.keys()) == {"metadata", "payload"}
    assert set(data["metadata"].keys()) == METADATA_KEYS
    required_payload_fields = {
        "user_id", "recipient_email", "report_type",
        "period_start", "period_end", "total_leads",
        "active_campaigns", "engagement_rate",
    }
    assert required_payload_fields <= set(data["payload"].keys())


def test_linkedin_disconnected_wire_format(linkedin_disconnected_message):
    body = serialize_message(linkedin_disconnected_message)
    data = json.loads(body)

    assert set(data.keys()) == {"metadata", "payload"}
    assert set(data["metadata"].keys()) == METADATA_KEYS
    required_payload_fields = {
        "user_id", "recipient_email", "disconnected_at",
        "reason", "reconnect_url", "affected_campaigns", "active_sequences",
    }
    assert required_payload_fields <= set(data["payload"].keys())


def test_delivery_failed_wire_format(delivery_failed_message):
    body = serialize_message(delivery_failed_message)
    data = json.loads(body)

    assert set(data.keys()) == {"metadata", "payload"}
    assert set(data["metadata"].keys()) == METADATA_KEYS
    required_payload_fields = {
        "user_id", "original_channel", "original_type",
        "error_message", "retry_count", "failed_at",
    }
    assert required_payload_fields <= set(data["payload"].keys())


def test_metadata_notification_id_is_uuid_string(reset_password_message):
    body = serialize_message(reset_password_message)
    data = json.loads(body)

    notification_id = data["metadata"]["notification_id"]
    assert isinstance(notification_id, str)
    assert len(notification_id) == 36


def test_metadata_created_at_is_iso_string(reset_password_message):
    body = serialize_message(reset_password_message)
    data = json.loads(body)

    created_at = data["metadata"]["created_at"]
    assert isinstance(created_at, str)
