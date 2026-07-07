### Incremental loads: only what's new

Reloading an entire source every run is slow and, for append-only data, wrong — you
re-insert rows you already have. **Incremental loading** processes only what changed
since last time, tracked by a **watermark**: the high-water mark of what's already
loaded (here, the latest `loaded_at`).

`raw.events` already holds day-1's events. The scaffold loads the whole feed again,
duplicating day-1. Fix it to append **only** events newer than the watermark:

```
INSERT INTO raw.events (event_id, name, loaded_at)
SELECT event_id, name, loaded_at
FROM landing.events_raw
WHERE loaded_at > (SELECT MAX(loaded_at) FROM raw.events);
```

After a correct incremental load `raw.events` has 5 events (3 old + 2 new) — not 8.
This watermark pattern is the backbone of real ingestion pipelines.

> Needs the stack: `./platform.sh up` first.
