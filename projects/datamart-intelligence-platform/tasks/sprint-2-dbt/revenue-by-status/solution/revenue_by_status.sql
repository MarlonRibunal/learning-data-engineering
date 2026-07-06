-- Reference solution (kept out of the learner's model path).
SELECT
    status,
    SUM(total_amount) AS revenue
FROM {{ source('raw', 'orders') }}
GROUP BY status
