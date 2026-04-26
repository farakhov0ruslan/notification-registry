import pytest

from notification_registry import NotificationType
from notification_registry import ProcessedNotification
from notification_registry.processors.base import BaseChannelProcessor
from notification_registry.processors.base import NotDefinedConvertMethod


class _FakeChannel(BaseChannelProcessor):
    @property
    def channel_name(self) -> str:
        return "fake"


def _make_processed(message):
    return ProcessedNotification(
        recipient="test@example.com",
        subject="Test",
        body="<html/>",
    )


def test_process_returns_none_when_skip_allowed(reset_password_message):
    processor = _FakeChannel(mapper={}, allow_skip_on_missing=True)

    result = processor.process(reset_password_message)

    assert result is None


def test_process_raises_when_type_missing_and_no_skip(reset_password_message):
    processor = _FakeChannel(mapper={}, allow_skip_on_missing=False)

    with pytest.raises(NotDefinedConvertMethod) as exc_info:
        processor.process(reset_password_message)

    assert "fake" in str(exc_info.value)
    assert "reset_password" in str(exc_info.value)


def test_process_calls_convert_fn_when_type_present(reset_password_message):
    processor = _FakeChannel(
        mapper={NotificationType.RESET_PASSWORD: _make_processed},
        allow_skip_on_missing=False,
    )

    result = processor.process(reset_password_message)

    assert isinstance(result, ProcessedNotification)
    assert result.recipient == "test@example.com"


def test_can_process_returns_true_for_supported_type(reset_password_message):
    processor = _FakeChannel(
        mapper={NotificationType.RESET_PASSWORD: _make_processed},
    )

    assert processor.can_process(NotificationType.RESET_PASSWORD) is True


def test_can_process_returns_false_for_unsupported_type():
    processor = _FakeChannel(mapper={})

    assert processor.can_process(NotificationType.ANALYTICS) is False


def test_supported_types_returns_list_of_types():
    processor = _FakeChannel(
        mapper={
            NotificationType.RESET_PASSWORD: _make_processed,
            NotificationType.ANALYTICS: _make_processed,
        },
    )

    supported = processor.supported_types()

    assert NotificationType.RESET_PASSWORD in supported
    assert NotificationType.ANALYTICS in supported
    assert len(supported) == 2


def test_supported_types_empty_mapper():
    processor = _FakeChannel(mapper={})

    assert processor.supported_types() == []


def test_not_defined_convert_method_message_contains_type_and_channel():
    exc = NotDefinedConvertMethod(NotificationType.RESET_PASSWORD, "fake_channel")

    assert "reset_password" in str(exc)
    assert "fake_channel" in str(exc)


def test_processed_notification_body_required():
    result = ProcessedNotification(recipient="test@example.com", body="<html/>")

    assert result.body == "<html/>"
    assert result.subject is None
    assert result.template_id is None
    assert result.template_data is None
