from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status


class CustomException:
    @staticmethod
    def uuid(ext: Exception) -> Response:
        return Response(
            {"detail": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST
        )


def custom_exception_handler(ext, content) -> None:
    if isinstance(ext, ValidationError) and "is not a valid UUID." in str(ext):
        return CustomException.uuid(ext=ext)
    print(type(ext), "\n", )
    return exception_handler(ext, content)
