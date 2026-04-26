"""Синхронный клиент для публикации NotificationMessage в RabbitMQ.

Поставляется как часть SDK: любой сервис, импортирующий notification_registry,
получает контракт сообщений и publisher. Сервис-отправитель не знает
имён очередей — маршрутизация определяется `message.metadata.channel.queue_name`.


Локальный режим (LocalNotificationClient) не подключается к RabbitMQ:
копит публикации в памяти и при желании зовёт in-process handler —
удобно для разработки без брокера и для тестов.
"""

from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Optional

from utils_library.RabbitMQ.publisher import RabbitPublisher
from utils_library.RabbitMQ.rabbitmq import RabbitMQConfig

from notification_registry.message import NotificationMessage
from notification_registry.serialization import serialize_message
from notification_registry.serialization import validate_message

LocalHandler = Callable[[str, bytes], None]


class NotificationClient(ABC):
    """Публикует NotificationMessage в очередь, соответствующую каналу.

    Сервис-отправитель работает только с этим интерфейсом и никогда
    не знает имён очередей — их определяет `NotificationChannel.queue_name`.
    Подмена реализации (Rabbit → Local) меняется одним вызовом фабрики.
    """

    def publish(self, message: NotificationMessage) -> None:
        validate_message(message)
        body = serialize_message(message)
        queue_name = message.metadata.channel.queue_name
        self._publish(queue_name=queue_name, body=body)

    @abstractmethod
    def _publish(self, queue_name: str, body: bytes) -> None: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    def __enter__(self) -> "NotificationClient":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


class RabbitMQNotificationClient(NotificationClient):
    """Обёртка над `utils_library.RabbitPublisher` (sync pika).

    Сам publisher — поток, поэтому start/close управляют его жизненным циклом.
    """

    def __init__(self, rabbit_config: Optional[RabbitMQConfig] = None) -> None:
        self._publisher = RabbitPublisher(rabbit_config=rabbit_config)

    def start(self) -> None:
        self._publisher.__enter__()

    def close(self) -> None:
        self._publisher.__exit__(None, None, None)

    def _publish(self, queue_name: str, body: bytes) -> None:
        self._publisher.publish(message=body.decode("utf-8"), queue=queue_name)


class LocalNotificationClient(NotificationClient):
    """Мок для локальной разработки и тестов.

    Не требует RabbitMQ. Сохраняет публикации в `self.published` и при
    наличии `handler` вызывает его — можно прокинуть in-process обработчик
    и запустить пайплайн без брокера.
    """

    def __init__(
        self,
        handler: Optional[LocalHandler] = None,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.handler = handler
        self._log = logger or (lambda _msg: None)
        self.published: list[tuple[str, bytes]] = []

    def start(self) -> None:
        self._log("LocalNotificationClient: started (no broker)")

    def close(self) -> None:
        self._log(
            f"LocalNotificationClient: closed "
            f"({len(self.published)} messages collected)"
        )

    def _publish(self, queue_name: str, body: bytes) -> None:
        self.published.append((queue_name, body))
        self._log(f"LocalNotificationClient → {queue_name} ({len(body)} bytes)")
        if self.handler is not None:
            self.handler(queue_name, body)


def provide_notification_client(
    environment: str,
    rabbit_config: Optional[RabbitMQConfig] = None,
    handler: Optional[LocalHandler] = None,
) -> NotificationClient:
    match environment:
        case "main":
            return RabbitMQNotificationClient(rabbit_config=rabbit_config)
        case _:
            return LocalNotificationClient(handler=handler)
