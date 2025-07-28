from paper4auth.models import User, Profile
from datetime import datetime
import json


class AuthenticationUtils:
    @staticmethod
    def registration_error(data: dict, exc: Exception) -> dict:
        return {
            "error": str(exc),
            "type": "auth.register.error",
            "timestamp": datetime.now().isoformat(),
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

            split_correlation_id: list = data["correlation_id"].split(".")
            return {
                "type": "auth.register.response",
                "data": {
                    "profile_created": profile_created,
                    "user_created": user_created,
                },
                "correlation_id": f"{split_correlation_id[0]}.{split_correlation_id[1]}.{int(split_correlation_id[2]) + 1}",
            }
        except Exception as exc:
            return AuthenticationUtils.registration_error(data=data, exc=exc)
