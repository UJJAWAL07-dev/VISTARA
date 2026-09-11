-- VISTARA Database
-- Spatial feature queries

-- Get all features for a project
SELECT
    id,
    project_id,
    dataset_id,
    job_id,
    feature_class,
    ST_AsGeoJSON(geometry) AS geometry,
    confidence,
    source,
    properties,
    created_at
FROM spatial_features
WHERE project_id = $1
ORDER BY created_at DESC;


-- Get features for a dataset
SELECT
    id,
    project_id,
    dataset_id,
    job_id,
    feature_class,
    ST_AsGeoJSON(geometry) AS geometry,
    confidence,
    source,
    properties,
    created_at
FROM spatial_features
WHERE dataset_id = $1
ORDER BY created_at DESC;


-- Get features by class
SELECT
    id,
    project_id,
    dataset_id,
    job_id,
    feature_class,
    ST_AsGeoJSON(geometry) AS geometry,
    confidence,
    source,
    properties,
    created_at
FROM spatial_features
WHERE project_id = $1
  AND feature_class = $2
ORDER BY created_at DESC;


-- Insert a spatial feature from GeoJSON
INSERT INTO spatial_features (
    id,
    project_id,
    dataset_id,
    job_id,
    feature_class,
    geometry,
    confidence,
    source,
    properties
)
VALUES (
    $1,
    $2,
    $3,
    $4,
    $5,
    ST_SetSRID(ST_GeomFromGeoJSON($6), 4326),
    $7,
    $8,
    COALESCE($9, '{}'::jsonb)
)
RETURNING
    id,
    feature_class,
    ST_AsGeoJSON(geometry) AS geometry,
    confidence,
    source,
    properties,
    created_at;


-- Spatial bounding-box query
SELECT
    id,
    project_id,
    dataset_id,
    job_id,
    feature_class,
    ST_AsGeoJSON(geometry) AS geometry,
    confidence,
    source,
    properties
FROM spatial_features
WHERE geometry && ST_MakeEnvelope(
    $1, $2, $3, $4, 4326
);


-- Count features by class
SELECT
    feature_class,
    COUNT(*) AS feature_count
FROM spatial_features
WHERE project_id = $1
GROUP BY feature_class
ORDER BY feature_class;