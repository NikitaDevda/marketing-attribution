WITH session_stages AS (
  SELECT 
    s.channel,
    s.landing_page,
    s.device,
    s.variant,
    COUNT(DISTINCT CASE WHEN e.event_type = 'session_start' THEN e.session_id END) AS session_start,
    COUNT(DISTINCT CASE WHEN e.event_type = 'product_view'  THEN e.session_id END) AS product_view,
    COUNT(DISTINCT CASE WHEN e.event_type = 'add_to_cart'   THEN e.session_id END) AS add_to_cart,
    COUNT(DISTINCT CASE WHEN e.event_type = 'checkout'      THEN e.session_id END) AS checkout,
    COUNT(DISTINCT CASE WHEN e.event_type = 'purchase'      THEN e.session_id END) AS purchase
  FROM sessions s
  JOIN events e ON s.session_id = e.session_id
  WHERE s.is_post_purchase = 0
  GROUP BY s.channel, s.landing_page, s.device, s.variant
)
SELECT *,
       ROUND(100.0 * product_view / NULLIF(session_start, 0), 2) AS view_rate_pct,
       ROUND(100.0 * checkout / NULLIF(add_to_cart, 0), 2)     AS cart_to_checkout_pct,
       ROUND(100.0 * purchase / NULLIF(session_start, 0), 2)     AS overall_cvr_pct
FROM session_stages
ORDER BY channel, overall_cvr_pct DESC;