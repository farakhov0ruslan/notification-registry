import re
from typing import Optional
from typing import Self
from uuid import UUID

from pydantic import AnyUrl
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import model_validator


class PhoneNumber(BaseModel):
    number: str

    @model_validator(mode="after")
    def validate_phone_number(self) -> Self:
        regex = r"8(?:-\d{3}){2}(?:-\d{2}){2}"
        if not re.match(regex, self.number):
            raise ValueError(f"Invalid phone number format: {self.number}")
        return self


class BaseNotificationPayload(BaseModel):
    """
    Базовая модель для payload любого уведомления
    Все конкретные payload должны наследоваться от этого класса
    """

    user_id: UUID = Field(..., description="ID пользователя получателя")
    recipient_email: Optional[EmailStr] = Field(
        None, description="Email получателя (обязателен для email-канала)"
    )
    recipient_phone: Optional[PhoneNumber] = Field(
        None, description="Телефон получателя (обязателен для whatsapp-канала)"
    )
    webhook_url: Optional[AnyUrl] = Field(
        None, description="URL вебхука (обязателен для webhook-канала)"
    )
