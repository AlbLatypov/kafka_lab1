from confluent_kafka import Producer, Consumer, serialization
import threading
import logging
import time

# Глобальные переменные Kafka
KAFKA_BOOTSTRAP_SERVERS = "kafka-0:9092" # адрес Kafka-брокера
KAFKA_TOPIC = "my-topic" # имя топика для обмена сообщениями

# Сериализаторы Kafka (UTF-8)
serializer = serialization.StringSerializer("utf_8")
deserializer = serialization.StringDeserializer("utf_8")

# Продюсер - отправляет сообщения каждую секунду
def producer():
    p = Producer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'acks': 'all', # подтверждение от всех реплик
        'retries': 5 # до 5 повторных попыток при сбое
    })

    i = 0
# Колбэк, вызывается при успешной/неудачной доставке
    def delivery_report(err, msg):
        if err:
            logging.error(f"Delivery failed: {err}")
        else:
            logging.info(f"Produced to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

    try:
        while True:
            message = f"Message {i}" # Простое текстовое сообщение
            # Отправка сообщения в Kafka с сериализацией в UTF-8
            p.produce(KAFKA_TOPIC, value=serializer(message), callback=delivery_report)
            p.poll(0)
            logging.info(f"Sent: {message}")
            i += 1
            time.sleep(1) # Задержка между отправками
    except KeyboardInterrupt:
        logging.info("Producer stopping...")
    finally:
        p.flush() # Дождаться отправки всех сообщений

# Single Consumer: читает по 1 сообщению, автокоммит
def single_consumer():
    c = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'single-consumer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    })

    c.subscribe([KAFKA_TOPIC]) # Подписка на топик
    
    try:
        while True:
            msg = c.poll(1.0) # Получение 1 сообщения
            if msg is None:
                continue
            if msg.error():
                logging.error(f"SingleConsumer error: {msg.error()}")
                continue
            try:
                value = deserializer(msg.value(), None) # Десериализация и обработка сообщения
                logging.info(f"SingleConsumer received: {value}")
            except Exception as e:
                logging.error(f"Deserialization error: {e}")
    except KeyboardInterrupt:
        logging.info("SingleConsumer stopping...")
    finally:
        c.close()

# Batch Consumer: читает пачками по 10, ручной коммит
def batch_consumer():
    c = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'batch-consumer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
        'fetch.wait.max.ms': 500,
        'fetch.min.bytes': 1
    })

    c.subscribe([KAFKA_TOPIC])
    try:
        while True:
            # Получение до 10 сообщений за один вызов
            msgs = c.consume(num_messages=10, timeout=1.0)
            if not msgs:
                continue
            for msg in msgs:
                if msg.error():
                    logging.error(f"BatchConsumer error: {msg.error()}")
                    continue
                try:
                    value = deserializer(msg.value(), None)
                    logging.info(f"BatchConsumer received: {value}")
                except Exception as e:
                    logging.error(f"Deserialization error: {e}")
            c.commit(asynchronous=False) # Коммит всех оффсетов сразу после обработки пачки
    except KeyboardInterrupt:
        logging.info("BatchConsumer stopping...")
    finally:
        c.close()

# Entrypoint
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(threadName)s] %(message)s')
    # 3 потока
    try:
        threads = [
            threading.Thread(target=producer, name="Producer"),
            threading.Thread(target=single_consumer, name="SingleConsumer"),
            threading.Thread(target=batch_consumer, name="BatchConsumer")
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    except KeyboardInterrupt:
        logging.info("Main thread interrupted. Exiting.")