-- SQLite
SELECT 'project' AS tbl, COUNT(*) AS n FROM project
UNION ALL SELECT 'element', COUNT(*) FROM element
UNION ALL SELECT 'dataset', COUNT(*) FROM dataset
UNION ALL SELECT 'model', COUNT(*) FROM model
UNION ALL SELECT 'feature', COUNT(*) FROM feature
UNION ALL SELECT 'tool', COUNT(*) FROM tool
UNION ALL SELECT 'evaluation', COUNT(*) FROM evaluation
UNION ALL SELECT 'observation', COUNT(*) FROM observation
UNION ALL SELECT 'metric', COUNT(*) FROM metric
UNION ALL SELECT 'measure', COUNT(*) FROM measure
UNION ALL SELECT 'datashape', COUNT(*) FROM datashape;
