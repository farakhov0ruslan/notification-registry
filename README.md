# Notification Registry SDK

Центральный SDK для работы с уведомлениями в Sales Trigger платформе.

## Описание

Notification Registry - это SDK библиотека, которая содержит:
- Типы уведомлений (NotificationType)
- Каналы доставки (NotificationChannel)
- Pydantic модели для payload каждого типа уведомлений
- Общий формат сообщений для RabbitMQ
- Функции сериализации/десериализации

Все сервисы системы уведомлений (notification-service, email-handler, platform-handler, webhook-handler, whatsapp-handler) используют этот SDK как общую зависимость.

## Установка

```bash
# Локальная разработка
pip install -e .

# Из приватного репозитория
pip install notification-registry
```

## Использование

### Создание и отправка уведомления (notification-service)

```python
from notification_registry import (
    NotificationMessage,
    NotificationMetadata,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    AnalyticsPayload,
)
from uuid import uuid4

# Создание payload
payload = AnalyticsPayload(
    user_id=uuid4(),
    recipient_email="user@example.com",
    report_type="weekly",
    period_start="2024-01-01T00:00:00Z",
    period_end="2024-01-07T23:59:59Z",
    total_leads=150,
    active_campaigns=5,
    engagement_rate=32.5,
)

# Создание метаданных
metadata = NotificationMetadata(
    notification_type=NotificationType.ANALYTICS,
    channel=NotificationChannel.EMAIL,
    priority=NotificationPriority.NORMAL,
)

# Создание сообщения
message = NotificationMessage(metadata=metadata, payload=payload)
```

### Сериализация для RabbitMQ

```python
from notification_registry import serialize_message, validate_message

# Валидация перед отправкой
validate_message(message)

# Сериализация в bytes
data = serialize_message(message)

# Получение routing key
routing_key = message.get_routing_key()  # "notification.email.normal"
priority = message.get_rabbitmq_priority()  # 5
```

### Десериализация и обработка в handler'ах

```python
from notification_registry import (
    deserialize_message,
    EmailChannelProcessor,
)

# В email-handler worker'е
def callback(ch, method, properties, body):
    # Десериализация
    message = deserialize_message(body)

    # Автоматически определится тип payload
    print(message.metadata.notification_type)  # NotificationType.ANALYTICS
    print(type(message.payload))  # AnalyticsPayload

    # Обработка через процессор
    processed = EmailChannelProcessor.process(message)

    # Получаем готовые данные для отправки
    print(processed.recipient)  # user_id
    print(processed.subject)  # "Weekly Analytics Report - Weekly"
    print(processed.template_id)  # "analytics_report"
    print(processed.template_data)  # {...}

    # Рендерим шаблон и отправляем email
    # ...
```

### Использование процессоров

Процессоры конвертируют общее `NotificationMessage` в формат специфичный для канала:

```python
from notification_registry import (
    EmailChannelProcessor,
    PlatformChannelProcessor,
    WebhookChannelProcessor,
    WhatsAppChannelProcessor,
)

# Email процессор
processed = EmailChannelProcessor.process(message)
# → recipient: user_id
# → subject: "..."
# → template_id: "analytics_report"
# → template_data: {...}

# Platform процессор
processed = PlatformChannelProcessor.process(message)
# → recipient: user_id
# → body: короткий текст для UI
# → extra: {"icon": "📊", "action_url": "..."}

# Webhook процессор
processed = WebhookChannelProcessor.process(message)
# → recipient: user_id
# → body: JSON строка для HTTP POST
# → extra: {"content_type": "application/json"}

# WhatsApp процессор
processed = WhatsAppChannelProcessor.process(message)
# → recipient: user_id
# → body: текст для WhatsApp
# → template_id: WhatsApp template name
```

## Типы уведомлений (MVP)

### ANALYTICS
Аналитические отчеты и статистика

**Payload**: `AnalyticsPayload`
- `report_type`: тип отчета (daily, weekly, monthly)
- `period_start`, `period_end`: период отчета
- `total_leads`, `active_campaigns`, `engagement_rate`: метрики

### RESET_PASSWORD
Сброс пароля пользователя

**Payload**: `ResetPasswordPayload`
- `reset_token`: токен для сброса
- `reset_url`: URL для сброса пароля
- `expires_at`: время истечения токена
- `user_name`: имя пользователя

### LINKEDIN_DISCONNECTED
Отключение LinkedIn аккаунта

**Payload**: `LinkedInDisconnectedPayload`
- `linkedin_profile_url`: URL профиля
- `disconnected_at`: время отключения
- `reason`: причина (session_expired, revoked, api_error)
- `reconnect_url`: URL для переподключения
- `affected_campaigns`, `active_sequences`: метрики

## Каналы доставки

- **EMAIL**: Email рассылка через SMTP/Mailgun
- **PLATFORM**: Внутренние уведомления на платформе (UI)
- **WEBHOOK**: HTTP POST на внешний URL
- **WHATSAPP**: WhatsApp Business API

## Приоритеты

- **LOW** (1): Низкий приоритет, можно батчить
- **NORMAL** (5): Стандартная обработка
- **HIGH** (8): Высокий приоритет
- **URGENT** (10): Критичные, обрабатываются немедленно

## Структура проекта

```
notification-registry/
├── notification_registry/
│   ├── __init__.py           # Главные экспорты
│   ├── types.py              # NotificationType enum
│   ├── channels.py           # NotificationChannel, NotificationPriority
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # BaseNotificationPayload
│   │   ├── analytics.py      # AnalyticsPayload
│   │   ├── password.py       # ResetPasswordPayload
│   │   └── linkedin.py       # LinkedInDisconnectedPayload
│   ├── message.py            # NotificationMessage
│   └── serialization.py      # serialize/deserialize
└── pyproject.toml
```

## Добавление нового типа уведомлений

1. Добавить в `types.py`:
```python
class NotificationType(StrEnum):
    WELCOME = "welcome"  # NEW
```

2. Создать payload модель в `models/welcome.py`:
```python
from notification_registry.models.base import BaseNotificationPayload

class WelcomePayload(BaseNotificationPayload):
    user_name: str
    company_name: str
```

3. Добавить в `models/__init__.py`:
```python
from notification_registry.models.welcome import WelcomePayload
```

4. Добавить в `serialization.py`:
```python
PAYLOAD_TYPE_MAPPING = {
    NotificationType.WELCOME: WelcomePayload,
    # ...
}
```

## Разработка

```bash
# Установка зависимостей
pip install -e ".[dev]"

# Запуск тестов
pytest

# Проверка типов
mypy notification_registry

# Линтинг
ruff check notification_registry
```

## Версионирование

- **0.1.0**: Начальная версия с MVP типами (Analytics, Reset Password, LinkedIn Disconnected)
- **0.2.0**: Добавление новых типов уведомлений (Welcome, Login, Billing)
- **1.0.0**: Production ready версия

## Лицензия

Proprietary - Sales Trigger Team