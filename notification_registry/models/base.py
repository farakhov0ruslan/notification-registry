from uuid import UUID

from pydantic import BaseModel, ValidationError, model_validator
from pydantic import Field
from pydantic import EmailStr, AnyUrl
import re

from typing import Self


class PhoneNumber(BaseModel):
    number: str

    @model_validator(mode='after')
    def validate_phone_number(self) -> Self:
        regex = r"8(?:-\\d{3}){2}(?:-\\d{2}){2}"
        if not re.match(regex, self.number):
            raise ValidationError(
                f'Invalid phone number format: {self.number}'
            )
        return self


class BaseNotificationPayload(BaseModel):
    """
    Базовая модель для payload любого уведомления
    Все конкретные payload должны наследоваться от этого класса
    """

    user_id: UUID = Field(..., description="ID пользователя получателя")
    recipient_email: EmailStr
    recipient_phone: PhoneNumber
    webhook_url: AnyUrl
