from gis_analysis.services import generate_full_report


def test_generate_full_report_end_to_end(predicted_gdf, ground_truth_gdf):
    report = generate_full_report(
        layer_name="parcels",
        predicted_gdf=predicted_gdf,
        ground_truth_gdf=ground_truth_gdf,
        run_landuse=True,
    )
    assert report["layer"] == "parcels"
    assert report["landuse"]["classification_mode"] == "ground_truth"
    assert report["scoring"]["mean_composite_score"] > 0
    assert report["overall"] is not None


def test_generate_full_report_without_ground_truth(predicted_gdf):
    report = generate_full_report(
        layer_name="ai_only_layer", predicted_gdf=predicted_gdf, run_landuse=True
    )
    assert report["statistics"] is None
    assert report["scoring"] is None
    assert report["landuse"]["classification_mode"] == "internal"