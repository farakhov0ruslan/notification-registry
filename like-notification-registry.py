# import json
# import typing
# from abc import ABC, abstractmethod
# from pydantic import BaseModel
# from enum import StrEnum
#
# # SDK
#
# class NotDefinedConvertMethod(Exception):
#     pass
#
#
# class NotificationType(str, StrEnum):
#     RESEND_PASSWORD = "resend_password"
#     FORGET_PASSWORD = "forget_password"
#     ANALYTICS = "analytics"
#     LOGIN = "login"
#     BILLING_PROBLEM = "billing_problem"
#
#
# T = typing.TypeVar("T", bound=BaseModel)
#
#
# class NotificationMetadata(BaseModel):
#     type: NotificationType
#     ...
#
#
# class GeneralNotificationObject(typing.Generic(T), BaseModel):
#     payload: bytes
#     metadata: NotificationMetadata
#
#     async def serialize(self, model: T) -> bytes:
#         pass
#
#     async def deserialize(self) -> T:
#         return json.loads(self.payload)
#
#
# class ImagePayload(BaseModel):
#     image_data: bytes
#
#
# class ImageNotificationObject(GeneralNotificationObject[ImagePayload]):
#     pass
#
#
# class SendWayProcessor:
#     def __init__(self, mapper: dict[NotificationType, typing.Callable[[GeneralNotificationObject]]],
#                  allow_to_skip_on_not_status: bool):
#         self.mapper = mapper
#         self._allow_to_skip = allow_to_skip_on_not_status
#
#     def convert_notification(self, notification: GeneralNotificationObject) -> None:
#         key_exists = notification.metadata.type in self.mapper
#         if not key_exists:
#             raise NotDefinedConvertMethod()
#         return self.mapper[notification.metadata.type](notification)
#
#
# # EMAIL
# try:
#     EmailWayProcessor.convert_notification()
# except NotDefinedConvertMethod:
#     pass
#
# # UTILS.py
# EmailWayProcessor = SendWayProcessor(
#     mapper={
#         NotificationType.LOGIN: lambda x: x,
#         NotificationType.RESEND_PASSWORD: lambda x: x,
#         NotificationType.FORGET_PASSWORD: lambda x: x,
#         NotificationType.ANALYTICS: lambda x: x,
#         NotificationType.LOGIN: lambda x: x,
#         NotificationType.BILLING_PROBLEM: lambda x: x,
#     }
# )
#
# # Site
# # EMAIL
# try:
#     SiteWayProcessor.convert_notification()
# except NotDefinedConvertMethod:
#     pass
#
#
# # UTILS.py
#
#
# async def process_login(message: ImageNotificationObject) -> typing.Any:
#     data = await message.deserialize()
#     message.serialize(model=)
#     data
#
#
# SiteWayProcessor = SendWayProcessor(
#     mapper={
#         NotificationType.LOGIN: lambda x: x,
#         NotificationType.RESEND_PASSWORD: lambda x: x,
#         NotificationType.FORGET_PASSWORD: lambda x: x,
#         NotificationType.ANALYTICS: lambda x: x,
#         NotificationType.LOGIN: lambda x: x,
#         NotificationType.BILLING_PROBLEM: lambda x: x,
#     }
# )
