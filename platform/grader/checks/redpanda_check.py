"""Streaming check: grade a learner's Kafka/Redpanda producer or consumer.

The learner writes a function; the grader runs it against the real broker and
verifies the result:

  mode: produce  — learner writes produce(bootstrap, topic, events); the grader
                   calls it, then consumes the topic and checks the events arrived.
  mode: consume  — learner writes consume(bootstrap, topic) -> list; the grader
                   produces known events, calls it, and checks what it returned.

    PASS  - the events round-tripped correctly
    FAIL  - the learner's code errored or produced/returned the wrong events
    ERROR - the broker was unreachable
"""

from __future__ import annotations

import importlib.util
import json

from ..context import Context
from ..registry import CheckType, register
from ..result import CheckResult

BOOTSTRAP_DEFAULT = "localhost:9092"
KNOWN_EVENTS = [
    {"order_id": 1, "status": "shipped", "amount": 100},
    {"order_id": 2, "status": "pending", "amount": 50},
    {"order_id": 3, "status": "shipped", "amount": 75},
]


def _load_fn(path, name):
    spec = importlib.util.spec_from_file_location("submission", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # may raise on bad learner code — caller catches
    return getattr(mod, name, None)


def _ids(events):
    return sorted(e.get("order_id") for e in events)


@register("redpanda")
class RedpandaCheck(CheckType):
    """Spec keys:
        mode: "produce" | "consume"
        bootstrap: broker address (default localhost:9092)
    """

    def run(self, ctx: Context) -> CheckResult:
        import os

        try:
            from kafka import KafkaConsumer, KafkaProducer
            from kafka.admin import KafkaAdminClient, NewTopic
            from kafka.errors import KafkaError, TopicAlreadyExistsError
        except ImportError:
            return self._error("kafka-python is not installed (platform/requirements.txt)")

        mode = self.spec.get("mode", "produce")
        bootstrap = self.spec.get("bootstrap") or os.environ.get(
            "REDPANDA_BOOTSTRAP", BOOTSTRAP_DEFAULT)
        topic = f"grade_{mode}_{os.getpid()}"

        # Load the learner's function (import errors are their fault → FAIL).
        try:
            fn = _load_fn(ctx.submission_path, mode)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your code failed to import: {exc}")
        if fn is None:
            return self._fail(f"define a function named `{mode}(...)` in your submission")

        # Ensure the topic exists (avoids auto-create timing races).
        try:
            admin = KafkaAdminClient(bootstrap_servers=bootstrap, request_timeout_ms=5000)
        except KafkaError:
            return self._error("can't reach Redpanda — start it: `docker compose up -d redpanda`")
        try:
            admin.create_topics([NewTopic(topic, num_partitions=1, replication_factor=1)])
        except TopicAlreadyExistsError:
            pass
        except Exception:  # noqa: BLE001
            pass
        finally:
            admin.close()

        if mode == "produce":
            return self._grade_produce(ctx, fn, bootstrap, topic, KafkaConsumer)
        return self._grade_consume(ctx, fn, bootstrap, topic, KafkaProducer)

    def _grade_produce(self, ctx, fn, bootstrap, topic, KafkaConsumer) -> CheckResult:
        try:
            fn(bootstrap, topic, [dict(e) for e in KNOWN_EVENTS])
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your producer errored: {exc}")

        consumer = KafkaConsumer(
            topic, bootstrap_servers=bootstrap, auto_offset_reset="earliest",
            consumer_timeout_ms=6000, value_deserializer=lambda b: json.loads(b),
        )
        got = [m.value for m in consumer]
        consumer.close()
        if len(got) != len(KNOWN_EVENTS):
            return self._fail(f"expected {len(KNOWN_EVENTS)} messages on the topic, "
                              f"found {len(got)} — did you send each event?")
        if _ids(got) != _ids(KNOWN_EVENTS):
            return self._fail("the messages don't match the events — send each event as JSON")
        return self._pass()

    def _grade_consume(self, ctx, fn, bootstrap, topic, KafkaProducer) -> CheckResult:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        for event in KNOWN_EVENTS:
            producer.send(topic, event)
        producer.flush()
        producer.close()

        try:
            got = fn(bootstrap, topic)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your consumer errored: {exc}")
        if not isinstance(got, list):
            return self._fail("consume(...) must return a list of the messages")
        try:
            ids = _ids(got)
        except (AttributeError, TypeError):
            return self._fail("each returned message should be a dict with an order_id")
        if ids != _ids(KNOWN_EVENTS):
            return self._fail(f"expected {len(KNOWN_EVENTS)} events back, got {len(got)} — "
                              "read all messages from the topic")
        return self._pass()
