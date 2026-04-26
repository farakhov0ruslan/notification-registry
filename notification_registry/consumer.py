from typing import Callable

from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from utils_library.Logging.log import get_logger
from utils_library.RabbitMQ.correct_consumer import RabbitConsumer
from utils_library.RabbitMQ.rabbitmq import RabbitMQConfig

LOGGER = get_logger(__name__)


class NotificationConsumer(RabbitConsumer):
    """
    RabbitMQ consumer with a callback for messages that exhaust retries.

    Channel handlers use this to publish a fallback notification, for example
    DELIVERY_FAILED to notification.platform.
    """

    def __init__(
        self,
        queue_name: str,
        on_message: Callable[[bytes], None],
        on_max_retries: Callable[[bytes], None],
        rabbitmq_config: RabbitMQConfig = None,
        ack_first: bool = False,
        max_fails: int = 20,
        max_retries: int | None = 5,
        retry_delay: float = 0.1,
    ):
        super().__init__(
            queue_name=queue_name,
            on_message=on_message,
            rabbitmq_config=rabbitmq_config,
            ack_first=ack_first,
            max_fails=max_fails,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )
        self._on_max_retries = on_max_retries

    def _retries_policy(
        self,
        channel: BlockingChannel,
        deliver: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        retries = (
            properties.headers.get("x-retry-count", 0) if properties.headers else 0
        )

        if self.max_retries and retries >= self.max_retries:
            LOGGER.error(
                f"Max retries ({self.max_retries}) reached for message, "
                f"invoking on_max_retries callback"
            )
            try:
                self._on_max_retries(body)
            except Exception as e:
                LOGGER.exception("on_max_retries callback failed", exc_info=e)
            if not self._ack_first:
                channel.basic_ack(deliver.delivery_tag)
            return

        super()._retries_policy(channel, deliver, properties, body)
