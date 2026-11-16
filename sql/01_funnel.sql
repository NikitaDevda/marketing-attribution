WITH f AS (
  SELECT e.event_type,
         COUNT(DISTINCT e.session_id) AS n,
         CASE e.event_type
           WHEN 'session_start' THEN 1
           WHEN 'product_view'  THEN 2
           WHEN 'add_to_cart'   THEN 3
           WHEN 'checkout'      THEN 4
           WHEN 'purchase'      THEN 5
         END AS step
  FROM events e
  JOIN sessions s ON e.session_id = s.session_id
  WHERE s.is_post_purchase = 0
  GROUP BY e.event_type
)
SELECT step,
       event_type,
       n,
       ROUND(100.0 * n / FIRST_VALUE(n) OVER (ORDER BY step), 2) AS pct_of_top,
       ROUND(100.0 * (LAG(n) OVER (ORDER BY step) - n)
             / NULLIF(LAG(n) OVER (ORDER BY step), 0), 2) AS drop_pct
FROM f
ORDER BY step;