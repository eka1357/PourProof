"""Tests for rebar grid and centerline detection."""

import pytest
from pourproof.vision.detection import detect_rebar_grid
from tests.fixtures.synthetic_generator import generate_synthetic_rebar_grid


def test_rebar_grid_detects_expected_bars():
    """Verify grid detection extracts horizontal and vertical bar candidates."""
    img, meta = generate_synthetic_rebar_grid()
    result = detect_rebar_grid(img)
    assert result.success is True
    # Synthetic grid has 3 vertical and 3 horizontal bars
    assert len(result.vertical_bars) >= 2
    assert len(result.horizontal_bars) >= 2

    # Verify positions are close to ground truth within bar thickness margin
    gt_x = meta["vertical_bar_positions_px"]
    for bar in result.vertical_bars:
        # Each detected bar should be close to one ground truth position
        min_dist = min(abs(bar.centerline_coord - x) for x in gt_x)
        assert min_dist <= 25.0, f"Detected bar at {bar.centerline_coord} too far from any GT: {gt_x}"
