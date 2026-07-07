### Consume events from a stream

A **consumer** reads events from a topic. Two settings matter for reading a finite
batch reliably: start at the **earliest** offset (so you see everything), and stop
after a **timeout** (so you don't block forever waiting for more).

**Your task:** finish `consume(bootstrap_servers, topic)` so it reads all messages on
`topic` and returns them as a list of dicts.

```python
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
```

> Needs the stack: `./platform.sh up` (Redpanda must be running).
