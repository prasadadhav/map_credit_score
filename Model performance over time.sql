-- SQLite
SELECT
  o.whenObserved AS ts,
  met.name       AS metric,
  CAST(ms.value AS REAL) AS value
FROM measure ms
JOIN metric met      ON met.id = ms.metric_id
JOIN observation o   ON o.id = ms.observation_id
JOIN element e       ON e.id = ms.measurand_id
WHERE e.type_spec = 'model'
  AND e.name = 'RandomForest'
  AND met.name IN ('ROCAUC','Accuracy','MCC','F1','Precision','Recall')
ORDER BY ts, metric;
