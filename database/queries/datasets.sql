-- VISTARA Database
-- Dataset queries

-- Get datasets for a project
SELECT
    id,
    project_id,
    name,
    dataset_type,
    description,
    status,
    file_path,
    format,
    crs,
    ST_AsGeoJSON(bounds) AS bounds,
    metadata,
    created_at,
    updated_at
FROM datasets
WHERE project_id = $1
ORDER BY created_at DESC;


-- Get dataset by ID
SELECT
    id,
    project_id,
    name,
    dataset_type,
    description,
    status,
    file_path,
    format,
    crs,
    ST_AsGeoJSON(bounds) AS bounds,
    metadata,
    created_at,
    updated_at
FROM datasets
WHERE id = $1;


-- Create dataset
INSERT INTO datasets (
    id,
    project_id,
    name,
    dataset_type,
    description,
    status,
    file_path,
    format,
    crs,
    bounds,
    metadata
)
VALUES (
    $1,
    $2,
    $3,
    $4,
    $5,
    COALESCE($6, 'pending'),
    $7,
    $8,
    $9,
    ST_GeomFromGeoJSON($10),
    COALESCE($11, '{}'::jsonb)
)
RETURNING
    id,
    project_id,
    name,
    dataset_type,
    description,
    status,
    file_path,
    format,
    crs,
    ST_AsGeoJSON(bounds) AS bounds,
    metadata,
    created_at,
    updated_at;


-- Update dataset status
UPDATE datasets
SET
    status = $2,
    updated_at = NOW()
WHERE id = $1
RETURNING
    id,
    project_id,
    name,
    status,
    updated_at;


-- Delete dataset
DELETE FROM datasets
WHERE id = $1;