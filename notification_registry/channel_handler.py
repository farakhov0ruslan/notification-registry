from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from typing import Callable

from utils_library.RabbitMQ.publisher import RabbitPublisher
from utils_library.RabbitMQ.rabbitmq import RabbitMQConfig

from notification_registry.channels import NotificationChannel
from notification_registry.channels import NotificationPriority
from notification_registry.consumer import NotificationConsumer
from notification_registry.message import NotificationMessage
from notification_registry.message import NotificationMetadata
from notification_registry.models.delivery_failed import DeliveryFailedPayload
from notification_registry.serialization import deserialize_message
from notification_registry.serialization import serialize_message
from notification_registry.types import NotificationType


@dataclass(frozen=True)
class ChannelHandlerSettings:
    channel: NotificationChannel
    max_retries: int = 5
    retry_delay: float = 2.0
    failed_error_message: str = "Notification delivery failed after all retries"

    @property
    def queue_name(self) -> str:
        return self.channel.queue_name


def build_delivery_failed_callback(
    *,
    publisher: RabbitPublisher,
    settings: ChannelHandlerSettings,
) -> Callable[[bytes, str | None], None]:
    def on_max_retries(body: bytes, error: str | None = None) -> None:
        original = deserialize_message(body)
        failed_msg = NotificationMessage(
            metadata=NotificationMetadata(
                notification_type=NotificationType.DELIVERY_FAILED,
                channel=NotificationChannel.PLATFORM,
                priority=NotificationPriority.HIGH,
            ),
            payload=DeliveryFailedPayload(
                user_id=original.payload.user_id,
                original_channel=settings.channel.value,
                original_type=str(original.metadata.notification_type),
                error_message=error or settings.failed_error_message,
                retry_count=settings.max_retries,
                failed_at=datetime.now(UTC),
            ),
        )

        publisher.publish(
            message=serialize_message(failed_msg).decode("utf-8"),
            queue=NotificationChannel.PLATFORM.queue_name,
            declare_queue=False,  # already declared with x-max-priority by the consumer
        )

    return on_max_retries


def create_channel_consumer(
    *,
    settings: ChannelHandlerSettings,
    on_message: Callable[[bytes], None],
    publisher: RabbitPublisher,
    rabbitmq_config: RabbitMQConfig,
) -> NotificationConsumer:
    return NotificationConsumer(
        queue_name=settings.queue_name,
        on_message=on_message,
        on_max_retries=build_delivery_failed_callback(
            publisher=publisher,
            settings=settings,
        ),
        rabbitmq_config=rabbitmq_config,
        max_retries=settings.max_retries,
        retry_delay=settings.retry_delay,
    )
