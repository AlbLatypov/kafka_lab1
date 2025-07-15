# Lab1 Kafka

### Инструкция по запуску

Файл репозитория `docker-compose.yml` используется для поднятия кластера и запуска приложения в 2х экземлярах.

1. Первый запуск для создания топика без самого приложения:

```bash
docker compose up kafka-0 kafka-1 kafka-2 ui -d
```

2. Переходим внутрь созданного контейнера, создаем топик:

```bash
$ docker exec -it kafka_lab1-kafka-0-1 bash
I have no name!@b08829ba2901:/$ kafka-topics.sh \
  --create \
  --topic my-topic \
  --bootstrap-server kafka-0:9092 \
  --partitions 3 \
  --replication-factor 2
Created topic my-topic.
I have no name!@b08829ba2901:/$
```

3. Посмотрим более подробную информацию о созданном топике:

```bash
$ kafka-topics.sh --describe --topic my-topic --bootstrap-server localhost:9092
Topic: my-topic TopicId: ztV95gXlSaOJjxA15sZU7g PartitionCount: 3       ReplicationFactor: 2    Configs:
        Topic: my-topic Partition: 0    Leader: 2       Replicas: 2,0   Isr: 2,0
        Topic: my-topic Partition: 1    Leader: 0       Replicas: 0,1   Isr: 0,1
        Topic: my-topic Partition: 2    Leader: 1       Replicas: 1,2   Isr: 1,2
```

Также данная информация отображена в файле topic.txt репозитория.


4. Далее запускаем приложение в двух экземлярях. Так как кафка кластер уже поднят, запустяться только они.

```bash
docker compose up -d
```

5. Смотрим логи

```bash
docker compose logs -f

application-1  | [BatchConsumer] BatchConsumer received: Message 30
application-1  | [Producer] Produced to my-topic [1] offset 22
application-1  | [Producer] Sent: Message 31
application-2  | [SingleConsumer] SingleConsumer received: Message 31
application-2  | [Producer] Produced to my-topic [0] offset 14
application-2  | [Producer] Sent: Message 31
application-1  | [SingleConsumer] SingleConsumer received: Message 31
application-2  | [BatchConsumer] BatchConsumer received: Message 31
application-1  | [BatchConsumer] BatchConsumer received: Message 31
application-1  | [Producer] Produced to my-topic [1] offset 23
application-1  | [Producer] Sent: Message 32
application-2  | [SingleConsumer] SingleConsumer received: Message 32
application-2  | [Producer] Produced to my-topic [2] offset 24
application-2  | [Producer] Sent: Message 32
application-1  | [SingleConsumer] SingleConsumer received: Message 32
application-2  | [BatchConsumer] BatchConsumer received: Message 32
application-1  | [BatchConsumer] BatchConsumer received: Message 32
application-1  | [Producer] Produced to my-topic [1] offset 24
application-1  | [Producer] Sent: Message 33
application-2  | [SingleConsumer] SingleConsumer received: Message 33
application-2  | [Producer] Produced to my-topic [2] offset 25
application-2  | [Producer] Sent: Message 33
application-2  | [SingleConsumer] SingleConsumer received: Message 33
application-1  | [BatchConsumer] BatchConsumer received: Message 33
application-1  | [BatchConsumer] BatchConsumer received: Message 33
application-1  | [Producer] Produced to my-topic [0] offset 15
application-1  | [Producer] Sent: Message 34
application-2  | [SingleConsumer] SingleConsumer received: Message 34

```

