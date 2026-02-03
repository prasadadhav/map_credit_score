-- SQLite
SELECT 'dataset' AS child, d.id
FROM dataset d
LEFT JOIN element e ON e.id = d.id
WHERE e.id IS NULL
UNION ALL
SELECT 'model', m.id
FROM model m
LEFT JOIN element e ON e.id = m.id
WHERE e.id IS NULL
UNION ALL
SELECT 'feature', f.id
FROM feature f
LEFT JOIN element e ON e.id = f.id
WHERE e.id IS NULL
UNION ALL
SELECT 'tool', t.id
FROM tool t
LEFT JOIN element e ON e.id = t.id
WHERE e.id IS NULL;
