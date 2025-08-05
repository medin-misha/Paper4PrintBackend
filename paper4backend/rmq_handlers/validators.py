from pydantic import BaseModel, validator
from typing import Literal, Dict
import re


# --- Базовые значения ---
class BaseMessage(BaseModel):
    type: str
    chat_id: str
    correlation_id: str


# --- Входящие запросы от Telegram Mini App ---
class PaymentInitRequest(BaseMessage):
    type: Literal["payment.init"]


class PaymentStatusData(BaseModel):
    status: Literal["PAID", "FAILED"]


class PaymentStatusRequest(BaseMessage):
    type: Literal["payment.status"]
    data: PaymentStatusData


class AuthRegistrationDataRequest(BaseModel):
    username: str


class AuthRegistrationDataResponse(BaseModel):
    profile_created: bool
    user_created: bool


class AuthRegistrationRequest(BaseMessage):
    data: AuthRegistrationDataRequest


class AuthRegistrationErrorResponse(BaseMessage):
    type: Literal["auth.register.response"] = "auth.register.response"
    error: str


class AuthRegistrationResponse(BaseMessage):
    data: AuthRegistrationDataResponse
    type: Literal["auth.register.response"] = "auth.register.response"


# --- Ответы от Django ---
class PaymentInitResponseData(BaseModel):
    currency: str
    amount: float
    name: str
    description: str


class PaymentInitResponse(BaseMessage):
    type: Literal["payment.init.response"] = "payment.init.response"
    data: PaymentInitResponseData


class PaymentStatusResponse(BaseMessage):
    type: Literal["payment.status.response"] = "payment.status.response"
    data: dict = {"status": "success"}


class PaymentErrorResponseData(BaseModel):
    error: str


class PaymentInitErrorResponse(BaseMessage):
    type: Literal["payment.init.response.error"] = "payment.init.response.error"
    data: PaymentErrorResponseData


class PaymentStatusErrorResponse(BaseMessage):
    type: Literal["payment.status.response.error"] = "payment.status.response.error"
    data: Dict[str, str]
