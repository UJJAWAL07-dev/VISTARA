-- VISTARA Database
-- Analysis result queries

-- Get analysis result for a job
SELECT
    id,
    job_id,
    statistics,
    issues,
    validation_status,
    validation_confidence,
    created_at
FROM analysis_results
WHERE job_id = $1
ORDER BY created_at DESC;


-- Create analysis result
INSERT INTO analysis_results (
    id,
    job_id,
    statistics,
    issues,
    validation_status,
    validation_confidence
)
VALUES (
    $1,
    $2,
    COALESCE($3, '{}'::jsonb),
    COALESCE($4, '[]'::jsonb),
    $5,
    $6
)
RETURNING
    id,
    job_id,
    statistics,
    issues,
    validation_status,
    validation_confidence,
    created_at;


-- Update validation result
UPDATE analysis_results
SET
    validation_status = $2,
    validation_confidence = $3
WHERE id = $1
RETURNING
    id,
    job_id,
    validation_status,
    validation_confidence,
    created_at;


-- Get analysis summary for a project
SELECT
    p.id AS project_id,
    p.name AS project_name,
    COUNT(DISTINCT sf.id) AS feature_count,
    COUNT(DISTINCT ar.id) AS analysis_count
FROM projects p
LEFT JOIN spatial_features sf
    ON sf.project_id = p.id
LEFT JOIN processing_jobs pj
    ON pj.project_id = p.id
LEFT JOIN analysis_results ar
    ON ar.job_id = pj.id
WHERE p.id = $1
GROUP BY p.id, p.name;