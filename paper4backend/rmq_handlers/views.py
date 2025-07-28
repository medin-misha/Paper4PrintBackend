import logging
from .base_rmq import BaseProducer
from .utils import AuthenticationUtils

log = logging.getLogger(__name__)


class AuthRegister(BaseProducer):
    queue = "queue2"

    def produce(self, ch, method, properties, body: bytes):
        log.info("Start processing message ")
        authentication_result: dict = AuthenticationUtils.create_user(raw_data=body)
        self.basic_publish(body=authentication_result)
        self.ack(ch=ch, method=method)
        log.info("Success processing message")
