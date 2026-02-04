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

## Использование 
Позже      