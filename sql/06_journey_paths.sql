SELECT path,
       COUNT(*) AS orders
FROM (
  SELECT order_id,
         GROUP_CONCAT(channel, ' > ') AS path
  FROM (
    SELECT o.order_id, s.channel
    FROM orders o
    JOIN sessions s ON s.user_id = o.user_id
     AND s.session_ts <= o.order_ts
     AND s.is_post_purchase = 0
    ORDER BY o.order_id, s.session_ts
  )
  GROUP BY order_id
)
GROUP BY path
ORDER BY orders DESC
LIMIT 15;