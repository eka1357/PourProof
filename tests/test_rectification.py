"""Tests for planar perspective rectification."""

import numpy as np
import pytest
from pourproof.vision.rectification import rectify_planar_view
from tests.fixtures.synthetic_generator import generate_synthetic_rebar_grid


def test_planar_rectification_success():
    """Verify rectification succeeds on valid marker corners and preserves dimensions."""
    img, _ = generate_synthetic_rebar_grid(marker_dimension_mm=50.0)
    # Marker is at (30, 30) with side 100px: [TL, TR, BR, BL]
    corners = [
        [30.0, 30.0],
        [130.0, 30.0],
        [130.0, 130.0],
        [30.0, 130.0],
    ]
    result = rectify_planar_view(
        image=img,
        marker_corners=corners,
        marker_dimension_mm=50.0,
    )

    assert result.success is True
    assert result.rectified_image is not None
    assert result.rectified_scale_mm_per_pixel is not None
    assert abs(result.rectified_scale_mm_per_pixel - 0.50) < 0.02
    assert result.homography_matrix is not None


def test_planar_rectification_rejects_invalid_corner_count():
    """Verify rectification safely fails if corners list is incomplete."""
    img, _ = generate_synthetic_rebar_grid()
    result = rectify_planar_view(
        image=img,
        marker_corners=[[0.0, 0.0], [10.0, 10.0]],  # Only 2 corners
        marker_dimension_mm=50.0,
    )
    assert result.success is False
    assert "INVALID_MARKER_GEOMETRY" in result.reason_codes


def test_planar_rectification_rejects_extreme_distortion():
    """Verify extreme perspective foreshortening triggers PERSPECTIVE_DISTORTION_TOO_HIGH."""
    img, _ = generate_synthetic_rebar_grid()
    # Pathological degenerate quadrilateral with near-collinear points
    degenerate_corners = [
        [30.0, 30.0],
        [130.0, 30.0],
        [130.0, 30.5],
        [30.0, 30.5],
    ]
    result = rectify_planar_view(
        image=img,
        marker_corners=degenerate_corners,
        marker_dimension_mm=50.0,
        max_expansion_ratio=2.0,
    )
    assert result.success is False
    assert any(code in result.reason_codes for code in ("PERSPECTIVE_DISTORTION_TOO_HIGH", "MARKER_DEGENERATE", "HOMOGRAPHY_ESTIMATION_FAILED"))
