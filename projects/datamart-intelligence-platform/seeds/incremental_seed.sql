-- Seed for the incremental-load task.
--
-- `landing.events_raw` is an append-only event feed with events from TWO days.
-- `raw.events` already holds day-1's events (a "previous load"). The learner must
-- append only the NEW (day-2) events — loading everything again would duplicate
-- day-1. Rebuilt each reseed for deterministic grading.

CREATE SCHEMA IF NOT EXISTS landing;
CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS landing.events_raw;
CREATE TABLE landing.events_raw (
    event_id  INTEGER,
    name      TEXT,
    loaded_at TIMESTAMP
);
INSERT INTO landing.events_raw (event_id, name, loaded_at) VALUES
    (1, 'signup',   '2026-03-01 00:00:00'),
    (2, 'login',    '2026-03-01 00:00:00'),
    (3, 'purchase', '2026-03-01 00:00:00'),
    (4, 'login',    '2026-03-02 00:00:00'),   -- new on day 2
    (5, 'purchase', '2026-03-02 00:00:00');   -- new on day 2

-- Target: day-1 events are already loaded.
DROP TABLE IF EXISTS raw.events;
CREATE TABLE raw.events (
    event_id  INTEGER,
    name      TEXT,
    loaded_at TIMESTAMP
);
INSERT INTO raw.events (event_id, name, loaded_at) VALUES
    (1, 'signup',   '2026-03-01 00:00:00'),
    (2, 'login',    '2026-03-01 00:00:00'),
    (3, 'purchase', '2026-03-01 00:00:00');
