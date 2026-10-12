"""Tests for planar calibration and metric scale estimation."""

import pytest
from pourproof.vision.calibration import detect_calibration_marker
from tests.fixtures.synthetic_generator import (
    generate_synthetic_rebar_grid,
    generate_missing_marker_fixture,
)


def test_calibration_marker_detected_accurately():
    """Verify known fiducial marker is detected and scale matches ground truth."""
    img, meta = generate_synthetic_rebar_grid(
        marker_dimension_mm=50.0,
        scale_mm_per_px=0.50,
    )
    result = detect_calibration_marker(img, marker_dimension_mm=50.0)
    assert result.valid is True
    assert result.marker_id == 0
    assert result.scale_mm_per_pixel is not None
    # Scale should be approximately 0.50 mm/px within 2% margin
    assert abs(result.scale_mm_per_pixel - 0.50) < 0.02
    assert result.marker_corners is not None
    assert len(result.marker_corners) == 4


def test_calibration_fails_when_marker_missing():
    """Verify calibration safely fails and abstains when no marker is present."""
    img, _ = generate_missing_marker_fixture()
    result = detect_calibration_marker(img, marker_dimension_mm=50.0)
    assert result.valid is False
    assert "CALIBRATION_MARKER_NOT_FOUND" in result.reason_codes
    assert result.scale_mm_per_pixel is None


def test_calibration_rejects_invalid_dimension():
    """Verify zero or negative marker dimension is rejected."""
    img, _ = generate_synthetic_rebar_grid()
    result = detect_calibration_marker(img, marker_dimension_mm=-10.0)
    assert result.valid is False
    assert "INVALID_MARKER_DIMENSION" in result.reason_codes
