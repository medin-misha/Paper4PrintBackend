### переменные окружения
В файле `./.env` ты должен вписать следующие переменные окружения:
```.env
SECRET_KEY="Секретный ключ базы django"
RABBITMQ_URL="amqps://логин:пароль@адресRabbitMQ"

# POSTGRESQL
POSTGRES_HOST = "хостPostgreSQL"
POSTGRES_PORT = "80085"
POSTGRES_USER = "юзернейм"
POSTGRES_PASSWORD = "пароль"
POSTGRES_DATABASE_NAME = "имя базы данных"  

# S3
CLOUDFlare_TOKEN_VALUE = "ЗАЧЕМНУЖНОЭТОВЕЛЬЮ"
CLOUDFLARE_SECRET_TOKEN = "АЯЕБУЧТОЭТОЗАТОКЕН"
CLOUDFLARE_ACCESS_TOKEN_ID = "ЯЕБУЭТОТТОКЕН"
CLOUDFLARE_ENDPOINT_URL = "https://эндпоинтurl.com"
CLOUDFLARE_BUCKET_NAME = "ИМЯЕБАТЬ"

# RabbitMq
RABBITMQ_URL = "amqps://LoGin:PaSsWord@dog.lmq.cloudamqp.com/WhatISIt"
RECEIVING_QUEUE
```
