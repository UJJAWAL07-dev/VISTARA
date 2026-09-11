from gis_analysis.reports import build_report


def test_build_report_fails_on_business_rule_violation():
    report = build_report(layer_name="parcels", business_rule_results=[
        {"rule": "no_overlap", "passed": False, "violation_count": 1}
    ])
    assert report["overall"]["status"] == "FAIL"
    assert "no_overlap" in report["overall"]["reasons"][0]


def test_build_report_none_when_no_basis_for_verdict():
    assert build_report(layer_name="roads", statistics_results={"mean_iou": 0.9})["overall"] is None


def test_build_report_passes_when_clean():
    report = build_report(layer_name="parcels", business_rule_results=[
        {"rule": "no_overlap", "passed": True, "violation_count": 0}
    ], scoring_results={"mean_composite_score": 0.8})
    assert report["overall"]["status"] == "PASS"