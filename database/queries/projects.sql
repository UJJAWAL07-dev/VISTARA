-- VISTARA Database
-- Project queries

-- Get all projects
SELECT
    id,
    name,
    description,
    status,
    created_at,
    updated_at
FROM projects
ORDER BY created_at DESC;


-- Get a project by ID
SELECT
    id,
    name,
    description,
    status,
    created_at,
    updated_at
FROM projects
WHERE id = $1;


-- Create a project
INSERT INTO projects (
    id,
    name,
    description,
    status
)
VALUES (
    $1,
    $2,
    $3,
    COALESCE($4, 'draft')
)
RETURNING
    id,
    name,
    description,
    status,
    created_at,
    updated_at;


-- Update project status
UPDATE projects
SET
    status = $2,
    updated_at = NOW()
WHERE id = $1
RETURNING
    id,
    name,
    description,
    status,
    created_at,
    updated_at;


-- Delete a project
DELETE FROM projects
WHERE id = $1;