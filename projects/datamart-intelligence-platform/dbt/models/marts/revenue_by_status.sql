-- SCAFFOLD (exercise stub). This is intentionally incomplete — it is the
-- starting point for the sprint-2-dbt / revenue-by-status task, so a fresh clone
-- does NOT pass the grader until you do the work.
--
-- Reset it back to this stub any time with:
--   ./scripts/check.sh start sprint-2-dbt revenue-by-status
--
-- TODO: return one row per order `status` with the total revenue for that status.
--       Read from {{ source('raw', 'orders') }}; revenue is SUM(total_amount).
SELECT
    'TODO' AS status,
    0 AS revenue
