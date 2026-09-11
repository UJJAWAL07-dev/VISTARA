# VISTARA GIS Analysis Engine

This package provides the analysis layer that consumes GIS-ready vector layers produced by the repository's GIS engine and computes:

- spatial relationship checks, overlap and containment discovery
- AI-vs-ground-truth validation reports with IoU matching
- statistics such as precision, recall, F1, and optional centroid offsets
- composite quality scoring with confidence and geometry validity weights
- land-use consistency and area-breakdown checks
- a single assembled report structure for backend or frontend consumption

## Phase 9 stabilization

The Phase 9 contract emphasizes safe inputs, typed failures, and a lightweight synthetic workflow:

1. Validate the shape of the incoming validation report before reading per-feature metrics.
2. Raise `InvalidInputError` for malformed or incompatible input rather than leaking `KeyError` or `ValueError`.
3. Provide a documented demo script and a report assembly example that localises the analysis package API.

## Quick start

From the repository root:

```bash
./.venv-1/bin/python -m gis_analysis.demo_workflow
./.venv-1/bin/python -m pytest gis_analysis/tests/ -v
```

The demonstration uses the same synthetic fixture generator already owned by the GIS engine so that the analysis package can be exercised independently without real input data.

## Main entry points

```python
from gis_analysis.services import (
    run_business_rule_checks,
    run_ai_validation,
    compute_accuracy_stats,
    compute_summary_stats,
    compute_composite_scores,
    run_landuse_analysis,
    generate_full_report,
)
```

The stable facade returns a single normalized report dictionary with sections for:

- `validation`: business-rule and AI-validation results
- `statistics`: computed accuracy summaries
- `scoring`: composite score breakdowns
- `landuse`: classification and area breakdown results
- `overall`: a high-level PASS/FAIL envelope derived from business-rule failures and scoring thresholds
