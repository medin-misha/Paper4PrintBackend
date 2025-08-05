from getopt import error

from django.db.models import QuerySet
from django.db import transaction
import json

from pydantic import ValidationError, BaseModel

from paper4auth.models import User, Profile
from shop.models import Orders, Payment
from shop.choices import OrderStatusChoices, PaidStatusChoices
from rmq_handlers.validators import (
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentInitResponseData,
    PaymentInitErrorResponse,
    PaymentStatusErrorResponse,
    PaymentStatusResponse, PaymentStatusRequest,
)


class BaseUtils:
    @staticmethod
    def increment_correlation_id(correlation_id: str) -> str:
        try:
            split_correlation_id: list = correlation_id.split(".")
            return f"{split_correlation_id[0]}.{split_correlation_id[1]}.{int(split_correlation_id[2]) + 1}"
        except ValueError:
            return f"You send invalid correlation id: {correlation_id}"
        except IndexError:
            return f"You send invalid correlation id: {correlation_id}"
        except AttributeError:
            return "Сorrelation_id not transmitted"

    @staticmethod
    def correlation_id_is_not_valid():
        pass

class AuthenticationUtils(BaseUtils):
    @staticmethod
    def registration_error(data: dict, exc: Exception) -> dict:
        return {
            "error": str(exc),
            "type": "auth.register.error",
            "correlation_id": data.get("correlation_id", "auth.register.N"),
        }

    @staticmethod
    def create_user(raw_data: bytes) -> dict:
        """
        Обрабатывает сообщение регистрации пользователя, полученное через RabbitMQ.

        Десериализует байтовое сообщение JSON, создает (или получает) пользователя и профиль
        на основе предоставленных данных. Возвращает ответ с результатами создания.

        Формат входного сообщения:
            {
                "chat_id": "123456789",
                "type": "auth.register",
                "data": {"username": "john_doe"},
                "timestamp": "2025-01-01T12:00:00Z",
                "correlation_id": "auth.register.1"
            }

        Возвращает словарь с типом ответа `auth.register.response` и новым `correlation_id`,
        увеличенным на 1, а также информацией о том, были ли созданы `User` и `Profile`.

        В случае ошибки возвращает объект с типом `auth.register.error`.

        Аргументы:
            raw_data (bytes): JSON-сообщение от RabbitMQ в байтовом виде.

        Возвращает:
            dict: Ответ в формате:
                {
                    "type": "auth.register.response",
                    "data": {
                        "user_created": bool,
                        "profile_created": bool
                    },
                    "correlation_id": "auth.register.2"
                }
                или
                {
                    "type": "auth.register.error",
                    "error": "Описание ошибки",
                    "timestamp": "2025-07-28T15:00:00",
                    "correlation_id": "auth.register.N"
                }

        Исключения:
            Внутри функции все исключения перехватываются и логируются через возврат ошибки.
        """
        try:
            data: dict = json.loads(raw_data)
            msg_data: dict = data.get("data", {})
            username: str = msg_data.get("username")
            chat_id: str = data.get("chat_id")
            if not username or not chat_id:
                raise ValueError("username and chat_id are required")
            user, user_created = User.objects.get_or_create(username=username)
            profile, profile_created = Profile.objects.get_or_create(
                chat_id=chat_id, user=user
            )

            correlation_id: list = AuthenticationUtils.increment_correlation_id(
                correlation_id=data["correlation_id"]
            )
            return {
                "type": "auth.register.response",
                "data": {
                    "profile_created": profile_created,
                    "user_created": user_created,
                },
                "correlation_id": correlation_id,
            }
        except Exception as exc:
            return AuthenticationUtils.registration_error(data=data, exc=exc)


class PaymentUtils(BaseUtils):

    @staticmethod
    def order_not_found(chat_id: str, correlation_id: str):
        return {
            "type": "payment.initial.response.error",
            "chat_id": chat_id,
            correlation_id: PaymentUtils.increment_correlation_id(
                correlation_id=correlation_id
            ),
            "data": {"error": f"Order is not found by {chat_id}."},
        }

    @staticmethod
    def get_order_queryset(chat_id: str) -> QuerySet[Orders]:
        return Orders.objects.filter(
            user__profiling__chat_id=chat_id, status=OrderStatusChoices.CREATED
        ).all()

    @staticmethod
    def initial_payment(
        raw_data: bytes,
    ) -> PaymentInitResponse or PaymentInitErrorResponse:
        try:
            data = PaymentInitRequest(**json.loads(raw_data))
        except ValidationError as error:
            return PaymentInitErrorResponse(
                chat_id="None",
                correlation_id="None",
                data={"error": f"{error}"},
            )
        chat_id: str = data.chat_id
        correlation_id: str = data.correlation_id
        try:
            order: QuerySet[Orders] = PaymentUtils.get_order_queryset(chat_id=chat_id).first()
            currency = order.payment.currency
            amount = order.payment.amount
            name = order.payment.name
            description = order.payment.description
        except AttributeError:
            return PaymentInitErrorResponse(
                type="payment.init.response.error",
                chat_id=chat_id,
                correlation_id=PaymentUtils.increment_correlation_id(
                    correlation_id=correlation_id
                ),
                data={"error": f"Order is not found by {chat_id}."},
            )


        return PaymentInitResponse(
            chat_id=chat_id,
            data=PaymentInitResponseData(
                currency=currency,
                amount=amount,
                name=name or "",
                description=description or "",
            ),
            correlation_id=PaymentUtils.increment_correlation_id(
                correlation_id=correlation_id
            ),
        )
    @staticmethod
    @transaction.atomic
    def set_paid_status(status: str, chat_id: str) -> None:
        order: QuerySet[Orders] = PaymentUtils.get_order_queryset(chat_id=chat_id)
        payment: Payment = order.first().payment
        if status == PaidStatusChoices.PAID:
            payment.status = PaidStatusChoices.PAID
            payment.save()
            order.first().status = OrderStatusChoices.PAID
            order.first().save()

    @staticmethod
    def status_payment(raw_data: bytes) -> PaymentStatusResponse | PaymentStatusErrorResponse:
        try:
            data = PaymentStatusRequest(**json.loads(raw_data))
        except ValidationError as error:
            return PaymentStatusErrorResponse(
                chat_id="None",
                correlation_id="None",
                data={"error": f"{error}"},
            )
        chat_id: str = data.chat_id
        correlation_id: str = data.correlation_id
        status = data.data.status
        try:
            PaymentUtils.set_paid_status(chat_id=chat_id, status=status)
            return PaymentStatusResponse(
                chat_id=chat_id,
                correlation_id=PaymentUtils.increment_correlation_id(
                    correlation_id=correlation_id
                )
            )
        except AttributeError:
            return PaymentStatusErrorResponse(
                chat_id=chat_id,
                correlation_id=PaymentUtils.increment_correlation_id(
                    correlation_id=correlation_id
                ),
                data={"error": f"Order is not found by {chat_id}."},
            )

        return PaymentStatusErrorResponse(
            chat_id=chat_id,
            correlation_id=PaymentUtils.increment_correlation_id(
                correlation_id=correlation_id
            ),
            data={"error": f"Status is invalid"},
        )
