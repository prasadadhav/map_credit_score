SELECT
  o.whenObserved AS ts,
  e.name         AS feature,
  CAST(ms.value AS REAL) AS value
FROM measure ms
JOIN metric met      ON met.id = ms.metric_id
JOIN observation o   ON o.id = ms.observation_id
JOIN element e       ON e.id = ms.measurand_id
WHERE met.name = 'wasserstein_distance'
  AND e.type_spec = 'feature'
ORDER BY ts, feature;
