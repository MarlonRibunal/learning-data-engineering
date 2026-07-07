-- Task: load only new data (incremental)
--
-- raw.events already holds day-1's events. This query re-loads EVERYTHING from the
-- feed every time — so day-1 gets loaded again and duplicated. Re-running a load
-- shouldn't reprocess what's already there.
--
-- TODO: append only the events NEWER than what's already in raw.events. A
--       "watermark" — the latest loaded_at already loaded — is how you do it.
INSERT INTO raw.events (event_id, name, loaded_at)
SELECT event_id, name, loaded_at
FROM landing.events_raw;
