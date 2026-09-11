-- VISTARA Database
-- Development seed data
--
-- This file inserts deterministic sample data for local development
-- and database integration testing.

BEGIN;

-- ============================================================
-- PROJECTS
-- ============================================================

INSERT INTO projects (
    id,
    name,
    description,
    status
)
VALUES
(
    '10000000-0000-0000-0000-000000000001',
    'Kolkata Urban Mapping',
    'Sample urban mapping project for development and GIS testing.',
    'completed'
),
(
    '10000000-0000-0000-0000-000000000002',
    'Urban Development Analysis',
    'Sample project for testing spatial analysis workflows.',
    'draft'
);

-- ============================================================
-- DATASETS
-- ============================================================

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
VALUES
(
    '20000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    'Kolkata Sample Vector Dataset',
    'vector',
    'Development vector dataset containing sample urban features.',
    'completed',
    'data/samples/kolkata.geojson',
    'GeoJSON',
    'EPSG:4326',
    ST_GeomFromText(
        'POLYGON((
            88.350 22.550,
            88.360 22.550,
            88.360 22.560,
            88.350 22.560,
            88.350 22.550
        ))',
        4326
    ),
    '{
        "source": "development",
        "resolution": "sample",
        "coordinate_system": "EPSG:4326"
    }'::jsonb
),
(
    '20000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000002',
    'Urban Analysis Sample',
    'vector',
    'Development dataset for testing GIS analysis.',
    'pending',
    NULL,
    'GeoJSON',
    'EPSG:4326',
    ST_GeomFromText(
        'POLYGON((
            88.340 22.540,
            88.350 22.540,
            88.350 22.550,
            88.340 22.550,
            88.340 22.540
        ))',
        4326
    ),
    '{
        "source": "development"
    }'::jsonb
);

-- ============================================================
-- PROCESSING JOBS
-- ============================================================

INSERT INTO processing_jobs (
    id,
    project_id,
    dataset_id,
    features,
    status,
    result,
    started_at,
    completed_at
)
VALUES
(
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    '[]'::jsonb,
    'completed',
    '{
        "feature_count": 3,
        "processing_type": "sample"
    }'::jsonb,
    NOW() - INTERVAL '10 minutes',
    NOW() - INTERVAL '5 minutes'
),
(
    '30000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000002',
    '20000000-0000-0000-0000-000000000002',
    '[]'::jsonb,
    'queued',
    NULL,
    NULL,
    NULL
);

-- ============================================================
-- SPATIAL FEATURES
-- ============================================================

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
VALUES
(
    '40000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    'building',
    ST_GeomFromText(
        'POLYGON((
            88.352 22.552,
            88.354 22.552,
            88.354 22.554,
            88.352 22.554,
            88.352 22.552
        ))',
        4326
    ),
    0.95,
    'sample_ai',
    '{
        "area_m2": 500,
        "height_m": 12.5,
        "model": "sample-building-detector"
    }'::jsonb
),
(
    '40000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    'parcel',
    ST_GeomFromText(
        'POLYGON((
            88.355 22.552,
            88.358 22.552,
            88.358 22.555,
            88.355 22.555,
            88.355 22.552
        ))',
        4326
    ),
    0.91,
    'sample_gis',
    '{
        "land_use": "residential"
    }'::jsonb
),
(
    '40000000-0000-0000-0000-000000000003',
    '10000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    'road',
    ST_GeomFromText(
        'LINESTRING(
            88.351 22.556,
            88.356 22.558,
            88.359 22.559
        )',
        4326
    ),
    0.88,
    'sample_gis',
    '{
        "road_type": "primary"
    }'::jsonb
);

-- ============================================================
-- ANALYSIS RESULTS
-- ============================================================

INSERT INTO analysis_results (
    id,
    job_id,
    statistics,
    issues,
    validation_status,
    validation_confidence
)
VALUES
(
    '50000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    '{
        "feature_count": 3,
        "building_count": 1,
        "parcel_count": 1,
        "road_count": 1
    }'::jsonb,
    '[]'::jsonb,
    'valid',
    0.93
);

COMMIT;