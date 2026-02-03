-- SQLite
-- datasets whose element.type_spec is not 'dataset'
SELECT d.id, e.type_spec, e.name
FROM dataset d
JOIN element e ON e.id = d.id
WHERE e.type_spec <> 'dataset'
UNION ALL
SELECT m.id, e.type_spec, e.name
FROM model m
JOIN element e ON e.id = m.id
WHERE e.type_spec <> 'model'
UNION ALL
SELECT f.id, e.type_spec, e.name
FROM feature f
JOIN element e ON e.id = f.id
WHERE e.type_spec <> 'feature'
UNION ALL
SELECT t.id, e.type_spec, e.name
FROM tool t
JOIN element e ON e.id = t.id
WHERE e.type_spec <> 'tool';
