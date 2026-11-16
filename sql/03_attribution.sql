WITH touches AS (
  SELECT o.order_id,
         o.revenue,
         s.channel,
         s.campaign,
         s.session_ts,
         ROW_NUMBER() OVER (PARTITION BY o.order_id ORDER BY s.session_ts ASC)  AS rn_first,
         ROW_NUMBER() OVER (PARTITION BY o.order_id ORDER BY s.session_ts DESC) AS rn_last,
         COUNT(*)     OVER (PARTITION BY o.order_id) AS n_touch
  FROM orders o
  JOIN sessions s ON s.user_id = o.user_id 
   AND s.session_ts <= o.order_ts
   AND s.is_post_purchase = 0
)
SELECT channel,
       ROUND(SUM(CASE WHEN rn_first = 1 THEN revenue ELSE 0 END), 2) AS first_touch_rev,
       ROUND(SUM(CASE WHEN rn_last  = 1 THEN revenue ELSE 0 END), 2) AS last_touch_rev,
       ROUND(SUM(revenue * 1.0 / n_touch), 2)                        AS linear_rev
FROM touches
GROUP BY channel
ORDER BY last_touch_rev DESC;