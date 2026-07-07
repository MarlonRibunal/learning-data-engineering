import json

from kafka import KafkaConsumer


def consume(bootstrap_servers, topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="earliest",
        consumer_timeout_ms=6000,
        value_deserializer=lambda b: json.loads(b),
    )
    messages = [record.value for record in consumer]
    consumer.close()
    return messages
