from typing import Callable

from pika import BasicProperties
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from utils_library.Logging.log import get_logger
from utils_library.RabbitMQ.correct_consumer import RabbitConsumer
from utils_library.RabbitMQ.rabbitmq import RabbitMQConfig

LOGGER = get_logger(__name__)

# Must match PriorityRabbitPublisher.MAX_PRIORITY in client.py
_MAX_QUEUE_PRIORITY = 10


class NotificationConsumer(RabbitConsumer):
    """
    RabbitMQ consumer with a callback for messages that exhaust retries.

    Channel handlers use this to publish a fallback notification, for example
    DELIVERY_FAILED to notification.platform.

    Declares queues with x-max-priority so RabbitMQ respects message priority.
    """

    def __init__(
        self,
        queue_name: str,
        on_message: Callable[[bytes], None],
        on_max_retries: Callable[[bytes, str | None], None],
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
        self._current_error: str | None = None

    def _connect(self) -> None:
        # Replicates RabbitConsumer._connect() but declares the queue with
        # x-max-priority so the broker honours per-message priority ordering.
        # Both consumer and publisher must agree on this argument — see
        # PriorityRabbitPublisher in client.py which does the same.
        LOGGER.info(
            {
                "message": "Connecting to RabbitMQ",
                "username": self._rabbit_config.username,
                "hosts": self._rabbit_config.hosts,
                "virtual_host": self._rabbit_config.virtual_host,
            }
        )
        self._connection = BlockingConnection(self._endpoints)
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count=1)
        self._channel.confirm_delivery()
        self._channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            auto_delete=False,
            arguments={"x-max-priority": _MAX_QUEUE_PRIORITY},
        )
        self._channel.basic_consume(
            on_message_callback=self.on_message, queue=self.queue_name
        )
        LOGGER.info(
            {
                "message": "Connected to RabbitMQ",
                "username": self._rabbit_config.username,
                "hosts": str(self._rabbit_config.hosts),
                "virtual_host": str(self._rabbit_config.virtual_host),
            }
        )

    def on_message(
        self,
        channel: BlockingChannel,
        deliver: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        self._current_error = None
        if self._ack_first:
            LOGGER.debug("RabbitMQ auto acknowledge message")
            channel.basic_ack(deliver.delivery_tag)
        try:
            self._on_message(body)
        except Exception as e:
            self._current_error = str(e)
            self._retries_policy(channel=channel, deliver=deliver, properties=properties, body=body)
            LOGGER.exception(f"Exception while processing message {body}", exc_info=e)
        else:
            if not self._ack_first:
                LOGGER.debug("RabbitMQ basic acknowledge after success callback")
                channel.basic_ack(deliver.delivery_tag)

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
                self._on_max_retries(body, self._current_error)
            except Exception as e:
                LOGGER.exception("on_max_retries callback failed", exc_info=e)
            if not self._ack_first:
                channel.basic_ack(deliver.delivery_tag)
            return

        super()._retries_policy(channel, deliver, properties, body)
