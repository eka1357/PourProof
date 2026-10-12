"""End-to-end tests for the deterministic inspection pipeline."""

import cv2
import pytest
from pourproof.vision.pipeline import run_inspection_pipeline
from tests.fixtures.synthetic_generator import (
    generate_synthetic_rebar_grid,
    generate_blurry_fixture,
    generate_missing_marker_fixture,
    generate_perspective_skewed_fixture,
)


def test_pipeline_normal_clean_fixture():
    """Verify normal calibrated image succeeds with status 'measured' and action 'DONE'."""
    img, meta = generate_synthetic_rebar_grid(
        nominal_spacing_mm=150.0,
        marker_dimension_mm=50.0,
        scale_mm_per_px=0.50,
    )

    result = run_inspection_pipeline(
        image_input=img,
        nominal_spacing_mm=150.0,
        tolerance_mm=15.0,
        calibration_marker_mm=50.0,
        session_id="test-session-001",
    )

    assert result["schema_version"] == "1.0"
    assert result["status"] == "measured"
    assert result["next_action"]["action"] == "DONE"
    assert result["quality_gate"]["accepted"] is True
    assert result["calibration"]["valid"] is True
    assert len(result["measurements"]) >= 2
    assert result["annotated_image_bytes"] is not None

    # Verify every measurement reports physical values and nominal values distinctly
    # Sub-millimeter synthetic tolerance justified by 0.50 mm/px resolution and subpixel corner refinement
    for m in result["measurements"]:
        assert m["nominal_spacing_mm"] == 150.0
        assert m["tolerance_mm"] == 15.0
        # Absolute error against 150.0mm ground truth must be < 0.20 mm (200 microns)
        assert abs(m["spacing_mm"] - 150.0) < 0.20, f"Measured {m['spacing_mm']} deviates from GT 150.0mm by > 0.20mm"
        assert m["in_tolerance"] is True

    # Verify inspectable trace records ordered steps
    trace = result["trace"]
    assert len(trace) >= 5
    tools = [step["tool"] for step in trace]
    assert "OpenCVRuntimeVerification" in tools
    assert "ImageQualityGate" in tools
    assert "MarkerCalibration" in tools
    assert "GridDetection" in tools
    assert "SpacingMeasurement" in tools


def test_pipeline_numerical_accuracy_multiple_spacings():
    """Verify sub-millimeter measurement accuracy across multiple design spacings (100mm, 200mm)."""
    for test_nominal in [100.0, 200.0]:
        img, meta = generate_synthetic_rebar_grid(
            nominal_spacing_mm=test_nominal,
            marker_dimension_mm=50.0,
            scale_mm_per_px=0.50,
        )
        res = run_inspection_pipeline(
            image_input=img,
            nominal_spacing_mm=test_nominal,
            tolerance_mm=10.0,
            calibration_marker_mm=50.0,
        )
        assert res["status"] == "measured"
        assert len(res["measurements"]) >= 2
        for m in res["measurements"]:
            err_vs_gt = abs(m["spacing_mm"] - test_nominal)
            assert err_vs_gt < 0.20, f"Spacing {test_nominal}mm had error {err_vs_gt}mm > 0.20mm"


def test_pipeline_raw_bytes_input():
    """Verify raw encoded PNG/JPEG bytes can be passed directly to the pipeline."""
    img, _ = generate_synthetic_rebar_grid()
    _, encoded = cv2.imencode(".png", img)
    raw_bytes = encoded.tobytes()

    result = run_inspection_pipeline(
        image_input=raw_bytes,
        nominal_spacing_mm=150.0,
        tolerance_mm=15.0,
        calibration_marker_mm=50.0,
    )

    assert result["status"] == "measured"
    assert result["next_action"]["action"] == "DONE"
    for m in result["measurements"]:
        assert abs(m["spacing_mm"] - 150.0) < 0.20


def test_pipeline_blurry_fixture_abstains():
    """Verify blurry image triggers abstention without fabricating measurements."""
    img, _ = generate_blurry_fixture()

    result = run_inspection_pipeline(
        image_input=img,
        nominal_spacing_mm=150.0,
        tolerance_mm=15.0,
        calibration_marker_mm=50.0,
    )

    assert result["status"] == "needs_recapture"
    assert result["next_action"]["action"] == "REQUEST_RECAPTURE"
    assert result["next_action"]["reason_code"] == "IMAGE_TOO_BLURRY"
    assert result["quality_gate"]["accepted"] is False
    assert len(result["measurements"]) == 0


def test_pipeline_missing_marker_abstains():
    """Verify uncalibrated image triggers recapture and refuses to guess."""
    img, _ = generate_missing_marker_fixture()

    result = run_inspection_pipeline(
        image_input=img,
        nominal_spacing_mm=150.0,
        tolerance_mm=15.0,
        calibration_marker_mm=50.0,
    )

    assert result["status"] == "needs_recapture"
    assert result["next_action"]["action"] == "REQUEST_RECAPTURE"
    assert result["next_action"]["reason_code"] == "CALIBRATION_MARKER_NOT_FOUND"
    assert result["calibration"]["valid"] is False
    assert len(result["measurements"]) == 0


def test_pipeline_out_of_tolerance_separates_gt_from_nominal():
    """Verify pipeline detects true physical spacing while comparing against nominal specification."""
    # Irregular spacing +35mm: Gap 1 is 185.0mm, Gap 2 is 115.0mm, Nominal is 150.0mm (+/- 10mm)
    img, meta = generate_synthetic_rebar_grid(
        nominal_spacing_mm=150.0,
        irregular_spacing_mm=35.0,
    )

    result = run_inspection_pipeline(
        image_input=img,
        nominal_spacing_mm=150.0,
        tolerance_mm=10.0,
        calibration_marker_mm=50.0,
    )

    assert result["status"] == "needs_review"
    assert result["next_action"]["action"] == "REVIEW_MEASUREMENT"
    assert result["summary"]["all_in_tolerance"] is False
    assert result["summary"]["out_of_tolerance_count"] >= 1

    # Check exact numerical values
    h_measurements = [m for m in result["measurements"] if m["direction"] == "horizontal_spacing"]
    assert len(h_measurements) == 2

    # H-01: true GT is 185.0mm
    h1 = h_measurements[0]
    assert abs(h1["spacing_mm"] - 185.0) < 0.20, f"H-01 measured {h1['spacing_mm']} vs GT 185.0mm"
    assert abs(h1["deviation_mm"] - 35.0) < 0.20, f"H-01 nominal deviation {h1['deviation_mm']} vs expected +35.0mm"
    assert h1["in_tolerance"] is False

    # H-02: true GT is 115.0mm
    h2 = h_measurements[1]
    assert abs(h2["spacing_mm"] - 115.0) < 0.20, f"H-02 measured {h2['spacing_mm']} vs GT 115.0mm"
    assert abs(h2["deviation_mm"] - (-35.0)) < 0.20, f"H-02 nominal deviation {h2['deviation_mm']} vs expected -35.0mm"
    assert h2["in_tolerance"] is False


def test_pipeline_extreme_perspective_skew_abstains():
    """Verify extreme perspective foreshortening rejects or abstains without false passes."""
    img, _ = generate_perspective_skewed_fixture()

    result = run_inspection_pipeline(
        image_input=img,
        nominal_spacing_mm=150.0,
        tolerance_mm=15.0,
        calibration_marker_mm=50.0,
    )

    # Must NOT report "measured" (false confidence)
    assert result["status"] in ("needs_recapture", "needs_review")
    if result["status"] == "needs_recapture":
        assert result["next_action"]["action"] == "REQUEST_RECAPTURE"


def test_pipeline_invalid_parameters_rejected():
    """Verify non-positive nominal spacing is immediately rejected."""
    img, _ = generate_synthetic_rebar_grid()

    result = run_inspection_pipeline(
        image_input=img,
        nominal_spacing_mm=-50.0,  # Invalid negative spacing
        tolerance_mm=10.0,
        calibration_marker_mm=50.0,
    )

    assert result["status"] == "rejected_input"
    assert result["next_action"]["action"] == "REQUEST_RECAPTURE"
    assert result["next_action"]["reason_code"] == "INVALID_INPUT_PARAMETERS"
