INSERT INTO raw.events (event_id, name, loaded_at)
SELECT event_id, name, loaded_at
FROM landing.events_raw
WHERE loaded_at > (SELECT MAX(loaded_at) FROM raw.events);
