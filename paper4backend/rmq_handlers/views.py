import logging
from django.conf import settings
from .base_rmq import BaseProducer
from .utils import AuthenticationUtils, PaymentUtils

log = logging.getLogger(__name__)


class AuthRegister(BaseProducer):
    queue = settings.REGISTRATION_SEND_QUEUE

    def produce(self, ch, method, properties, body: bytes):
        authentication_result: dict = AuthenticationUtils.create_user(raw_data=body)
        self.basic_publish(body=authentication_result)
        self.ack(ch=ch, method=method)

class PaymentInitial(BaseProducer):
    queue = settings.PAYMENT_SEND_QUEUE

    def produce(self, ch, method, properties, body: bytes):
        response = PaymentUtils.initial_payment(raw_data=body)
        print(response)
        self.basic_publish(body=response)
        self.ack(ch=ch, method=method)

class PaymentStatus(BaseProducer):
    queue = settings.PAYMENT_SEND_QUEUE

    def produce(self, ch, method, properties, body: bytes):
        PaymentUtils.status_payment(raw_data=body)
        print("OK")
        self.ack(ch=ch, method=method)