from django.conf import settings
import pika
import json

class BaseRMQ:
    """
    Базовый класс для взаимодействия с RabbitMQ.

    Предоставляет функционал подключения и работы с каналом RabbitMQ.
    Сам по себе не предназначен для использования — должен быть унаследован
    классом, в котором определена переменная `queue` с названием очереди.

    Атрибуты:
        connection (pika.BlockingConnection): Подключение к RabbitMQ. (Переменная RMQ_URL в переменных окружения)
        channel (pika.channel.Channel): Канал для операций с очередями.

    Methods:
        queue_declare(): Объявляет очередь, имя которой должно быть задано
                         в дочернем классе в атрибуте `queue`.
    """
    connection = pika.BlockingConnection(pika.URLParameters(settings.RMQ_URL))
    channel = connection.channel()

    def queue_declare(self):
        self.channel.queue_declare(queue=self.queue)


class BaseConsumer(BaseRMQ):
    """
    Базовый класс-консьюмер для чтения сообщений из очереди RabbitMQ.

    Упрощает работу с получением сообщений из очереди, имя которой передаётся
    при инициализации (обычно из `django.conf.settings`).

    Предназначен для наследования: дочерний класс должен переопределить
    метод `callback()` — логику обработки входящих сообщений.

    Args:
        queue (str): Имя очереди RabbitMQ, из которой будут приниматься сообщения.

    Methods:
        callback(ch, method, properties, body): Метод-обработчик сообщений из
            очереди (должен быть реализован в дочернем классе).
        consuming(): Запускает бесконечное чтение очереди; останавливается
            по KeyboardInterrupt и закрывает соединение.
    """
    def __init__(self, queue: str):
        self.queue = queue

    def callback(self, ch, method, properties, body) -> None:
        pass

    def consuming(self) -> None:
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.connection.close()


class BaseProducer(BaseRMQ):
    """
    Базовый класс-продюсер для отправки сообщений в RabbitMQ.

    Предназначен для наследования во View (или других слоях), где в дочернем
    классе должен быть переопределён атрибут `queue` с именем очереди.

    Предоставляет метод `basic_publish()` для публикации сообщений в указанную
    очередь (с сериализацией dict → JSON), а также вспомогательные методы для
    подтверждения доставки и закрытия канала.

    Attributes:
        queue (str): Имя очереди RabbitMQ (должно быть определено в наследнике).

    Methods:
        basic_publish(body, exchange=""): Публикует сообщение в очередь.
        close(): Закрывает канал RabbitMQ.
        produce(...): Заготовка под сложную логику отправки (переопределяется при необходимости).
        ack(ch, method, ...): Подтверждает доставку сообщения.
    """
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
