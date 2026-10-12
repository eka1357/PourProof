"""Tests for spacing measurements and tolerance evaluation."""

import pytest
from pourproof.vision.measurement import compute_rebar_spacings


def test_measurements_match_known_spacings():
    """Verify physical spacing computation matches known ground truth."""
    # 3 bars at x=250, 550, 850 (300px spacing). Scale = 0.50 mm/px -> 150.0 mm
    v_pos = [250.0, 550.0, 850.0]
    h_pos = [250.0, 550.0, 850.0]
    scale = 0.50
    nominal = 150.0
    tolerance = 10.0

    result = compute_rebar_spacings(
        vertical_bar_positions=v_pos,
        horizontal_bar_positions=h_pos,
        scale_mm_per_pixel=scale,
        nominal_spacing_mm=nominal,
        tolerance_mm=tolerance,
    )

    assert result.success is True
    assert len(result.measurements) == 4  # 2 horizontal gaps + 2 vertical gaps
    assert result.summary is not None
    assert result.summary.all_in_tolerance is True
    assert result.summary.in_tolerance_count == 4
    assert result.summary.out_of_tolerance_count == 0

    for m in result.measurements:
        assert abs(m.spacing_mm - 150.0) < 0.1
        assert abs(m.deviation_mm) < 0.1
        assert m.in_tolerance is True


def test_out_of_tolerance_gap_flagged():
    """Verify gap exceeding tolerance is correctly flagged as out of tolerance."""
    # Second vertical gap is 350px = 175mm (nominal 150mm +/- 10mm -> out of tolerance)
    v_pos = [250.0, 550.0, 900.0]
    h_pos = [250.0, 550.0]
    scale = 0.50
    nominal = 150.0
    tolerance = 10.0

    result = compute_rebar_spacings(
        vertical_bar_positions=v_pos,
        horizontal_bar_positions=h_pos,
        scale_mm_per_pixel=scale,
        nominal_spacing_mm=nominal,
        tolerance_mm=tolerance,
    )

    assert result.success is True
    assert result.summary is not None
    assert result.summary.all_in_tolerance is False
    assert result.summary.out_of_tolerance_count == 1
    # Check that H-02 is out of tolerance
    h2 = next(m for m in result.measurements if m.measurement_id == "H-02")
    assert h2.in_tolerance is False
    assert h2.spacing_mm == 175.0
    assert h2.deviation_mm == 25.0


def test_measurement_asymmetric_gaps():
    """Verify measurement correctly calculates varying intervals in the same mat."""
    v_pos = [100.0, 300.0, 600.0]  # Gap 1: 200px = 100mm, Gap 2: 300px = 150mm at scale 0.5
    h_pos = [100.0, 400.0]         # Gap: 300px = 150mm
    scale = 0.50
    nominal = 150.0
    tolerance = 10.0

    result = compute_rebar_spacings(
        vertical_bar_positions=v_pos,
        horizontal_bar_positions=h_pos,
        scale_mm_per_pixel=scale,
        nominal_spacing_mm=nominal,
        tolerance_mm=tolerance,
    )

    assert result.success is True
    assert len(result.measurements) == 3
    # H-01: 100mm (out of tolerance vs 150mm)
    assert result.measurements[0].spacing_mm == 100.0
    assert result.measurements[0].in_tolerance is False
    # H-02: 150mm (in tolerance)
    assert result.measurements[1].spacing_mm == 150.0
    assert result.measurements[1].in_tolerance is True
    # V-01: 150mm (in tolerance)
    assert result.measurements[2].spacing_mm == 150.0
    assert result.measurements[2].in_tolerance is True


def test_measurement_fails_on_insufficient_bars():
    """Verify measurement fails cleanly when only 1 bar is provided."""
    result = compute_rebar_spacings(
        vertical_bar_positions=[100.0],
        horizontal_bar_positions=[100.0],
        scale_mm_per_pixel=0.50,
        nominal_spacing_mm=150.0,
        tolerance_mm=10.0,
    )
    assert result.success is False
    assert "NO_SPACINGS_MEASURABLE" in result.reason_codes
