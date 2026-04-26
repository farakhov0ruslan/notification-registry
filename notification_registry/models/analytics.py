from datetime import datetime
from typing import Optional

from pydantic import Field

from notification_registry.models.base import BaseNotificationPayload


class AnalyticsPayload(BaseNotificationPayload):
    """
    Payload для аналитических отчетов и статистики
    """

    report_type: str = Field(
        ..., description="Тип отчета (daily, weekly, monthly)"
    )
    period_start: datetime = Field(..., description="Начало периода отчета")
    period_end: datetime = Field(..., description="Конец периода отчета")
    total_leads: int = Field(..., description="Общее количество лидов")
    active_campaigns: int = Field(..., description="Количество активных кампаний")
    engagement_rate: float = Field(..., description="Показатель вовлеченности")
    report_url: Optional[str] = Field(
        None, description="URL для просмотра полного отчета"
    )
