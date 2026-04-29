from typing import Optional

from pydantic import Field

from notification_registry.models.base import BaseNotificationPayload


class CampaignStatusPayload(BaseNotificationPayload):
    """
    Payload уведомления об изменении статуса кампании.
    """

    campaign_id: str
    campaign_name: str
    status: str = Field(..., description="started | paused | completed | failed")
    leads_processed: Optional[int] = None
    campaign_url: Optional[str] = None
