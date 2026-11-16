WITH last_touch AS (
  SELECT o.order_id,
         o.user_id,
         o.revenue,
         s.channel,
         s.campaign,
         ROW_NUMBER() OVER (PARTITION BY o.order_id ORDER BY s.session_ts DESC) AS rn
  FROM orders o
  JOIN sessions s ON s.user_id = o.user_id 
   AND s.session_ts <= o.order_ts
   AND s.is_post_purchase = 0
),
rev AS (
  SELECT channel,
         campaign,
         SUM(revenue) AS revenue,
         COUNT(DISTINCT user_id) AS customers,
         COUNT(DISTINCT order_id) AS orders
  FROM last_touch
  WHERE rn = 1
  GROUP BY channel, campaign
),
sp AS (
  SELECT channel,
         campaign,
         SUM(spend) AS spend
  FROM ad_spend
  GROUP BY channel, campaign
)
SELECT sp.channel,
       sp.campaign,
       ROUND(COALESCE(r.revenue, 0), 2) AS revenue,
       ROUND(sp.spend, 2)               AS spend,
       COALESCE(r.customers, 0)         AS customers,
       COALESCE(r.orders, 0)            AS orders,
       ROUND(COALESCE(r.revenue, 0) / NULLIF(sp.spend, 0), 2)     AS roas,
       ROUND(sp.spend / NULLIF(r.customers, 0), 2)                AS cac
FROM sp
LEFT JOIN rev r ON sp.channel = r.channel AND sp.campaign = r.campaign
ORDER BY roas DESC;