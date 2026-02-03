-- SQLite
-- How many distinct observation timestamps?
SELECT COUNT(*) AS obs_rows, COUNT(DISTINCT whenObserved) AS distinct_times
FROM observation;

-- Are measures spread across many observations?
SELECT COUNT(DISTINCT observation_id) AS distinct_obs_ids, COUNT(*) AS measures
FROM measure;

-- Example: one drift metric over time (replace metric_id accordingly)
SELECT o.whenObserved, m.metric_id, m.value
FROM measure m
JOIN observation o ON o.id = m.observation_id
WHERE m.metric_id = 1
ORDER BY o.whenObserved;
