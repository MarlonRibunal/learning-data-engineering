### Produce events to a stream

A **producer** publishes events to a topic. Downstream, any number of consumers can
read them independently — that decoupling is what makes streaming scale.

**Your task:** finish `produce(bootstrap_servers, topic, events)` so it sends each
event in `events` to `topic`. Serialize each event to JSON bytes.

```python
import json
from kafka import KafkaProducer

def produce(bootstrap_servers, topic, events):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    for event in events:
        producer.send(topic, event)
    producer.flush()   # don't forget to flush!
    producer.close()
```

`flush()` matters — without it your program can exit before the events are actually
sent.

> Needs the stack: `./platform.sh up` (Redpanda must be running).
