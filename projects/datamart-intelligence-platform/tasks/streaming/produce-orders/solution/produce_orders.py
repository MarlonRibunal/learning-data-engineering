import json

from kafka import KafkaProducer


def produce(bootstrap_servers, topic, events):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    for event in events:
        producer.send(topic, event)
    producer.flush()
    producer.close()
