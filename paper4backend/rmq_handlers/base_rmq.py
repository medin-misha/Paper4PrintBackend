from django.conf import settings
import pika
import json

class BaseRMQ:
    connection = pika.BlockingConnection(pika.URLParameters(settings.RMQ_URL))
    channel = connection.channel()

    def queue_declare(self):
        self.channel.queue_declare(queue=self.queue)


class BaseConsumer(BaseRMQ):
    queue = settings.RECEIVING_QUEUE

    def callback(self, ch, method, properties, body) -> None:
        pass

    def consuming(self) -> None:
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.connection.close()


class BaseProducer(BaseRMQ):
    queue = ""

    def basic_publish(self, body: dict, exchange: str = ""):
        self.queue_declare()
        print(body)
        self.channel.basic_publish(routing_key=self.queue, exchange=exchange, body=json.dumps(body))

    def close(self):
        self.channel.close()

    def produce(self, ch, method, properties, body):
        pass

    def ack(self, ch, method, properties=None, body=None):
        ch.basic_ack(delivery_tag=method.delivery_tag)
