SELECT s.landing_page AS dimension,
       COUNT(DISTINCT s.session_id) AS sessions,
       COUNT(DISTINCT CASE WHEN e.event_type = 'product_view' THEN s.session_id END) AS viewed,
       COUNT(DISTINCT CASE WHEN e.event_type = 'add_to_cart'  THEN s.session_id END) AS carted,
       COUNT(DISTINCT CASE WHEN e.event_type = 'checkout'     THEN s.session_id END) AS checkout,
       COUNT(DISTINCT CASE WHEN e.event_type = 'purchase'     THEN s.session_id END) AS purchases,
       ROUND(100.0 * (1.0 - COUNT(DISTINCT CASE WHEN e.event_type = 'product_view' THEN s.session_id END) * 1.0
             / NULLIF(COUNT(DISTINCT s.session_id), 0)), 2) AS bounce_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN s.session_id END) * 1.0
             / NULLIF(COUNT(DISTINCT s.session_id), 0), 2) AS conv_pct
FROM sessions s
JOIN events e ON e.session_id = s.session_id
WHERE s.is_post_purchase = 0
GROUP BY 1
ORDER BY bounce_pct DESC;