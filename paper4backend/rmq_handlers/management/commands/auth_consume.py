from django.core.management.base import BaseCommand
from django.conf import settings
import json
from rmq_handlers.base_rmq import BaseConsumer, BaseProducer
from rmq_handlers.urls import urlpatterns


class Command(BaseCommand):
    help = "Consume messages from RabbitMQ"

    def callback(
        self,
        ch: "BlockingChannel",
        method: "Basic.Deliver",
        properties: "BasicProperties",
        body: bytes,
    ) -> None:
        dict_body: dict = json.loads(body)
        queue_name = dict_body.get("type")
        producer: BaseProducer = urlpatterns.get(queue_name)
        producer().produce(ch=ch, method=method, properties=properties, body=body)


    def handle(self, *args, **kwargs) -> None:
        consumer = BaseConsumer(queue=settings.REGISTRATION_RECEIVING_QUEUE)
        consumer.queue_declare()
        consumer.channel.basic_consume(queue=consumer.queue, on_message_callback=self.callback)
        consumer.consuming()
