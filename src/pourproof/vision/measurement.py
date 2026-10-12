"""Rebar spacing measurement and tolerance evaluation module.

Calculates physical adjacent center-to-center distances, preserves pixel-level
evidence, and compares measurements against user-entered specifications.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import numpy as np


@dataclass
class SpacingMeasurement:
    measurement_id: str
    direction: str  # "horizontal_spacing" (between vertical bars) or "vertical_spacing" (between horizontal bars)
    bar_index_start: int
    bar_index_end: int
    pixel_spacing: float
    spacing_mm: float
    nominal_spacing_mm: float
    deviation_mm: float
    tolerance_mm: float
    in_tolerance: bool
    measurement_quality: str  # "high", "acceptable", "uncertain"
    evidence_region: Dict[str, Any]


@dataclass
class MeasurementSummary:
    total_gaps_measured: int
    in_tolerance_count: int
    out_of_tolerance_count: int
    all_in_tolerance: bool
    mean_spacing_mm: Optional[float] = None
    min_spacing_mm: Optional[float] = None
    max_spacing_mm: Optional[float] = None
    std_spacing_mm: Optional[float] = None
    max_abs_deviation_mm: Optional[float] = None


@dataclass
class SpacingEvaluationResult:
    success: bool
    measurements: List[SpacingMeasurement] = field(default_factory=list)
    summary: Optional[MeasurementSummary] = None
    warnings: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)


def compute_rebar_spacings(
    vertical_bar_positions: List[float],
    horizontal_bar_positions: List[float],
    scale_mm_per_pixel: float,
    nominal_spacing_mm: float,
    tolerance_mm: float,
    uncertainty_threshold_ratio: float = 0.25,
) -> SpacingEvaluationResult:
    """Compute physical adjacent bar spacings and evaluate against nominal specification.
    
    Args:
        vertical_bar_positions: Sorted x-coordinates of vertical bars.
        horizontal_bar_positions: Sorted y-coordinates of horizontal bars.
        scale_mm_per_pixel: Physical metric scale factor (mm/px).
        nominal_spacing_mm: User-entered nominal design spacing.
        tolerance_mm: User-entered allowable tolerance (+/- mm).
        uncertainty_threshold_ratio: Spacing anomaly ratio flagging uncertain measurement.
        
    Returns:
        SpacingEvaluationResult with list of individual measurements and summary statistics.
    """
    if scale_mm_per_pixel <= 0:
        return SpacingEvaluationResult(
            success=False,
            reason_codes=["INVALID_SCALE_FACTOR"],
            warnings=["Scale factor must be strictly positive."],
        )
    if nominal_spacing_mm <= 0:
        return SpacingEvaluationResult(
            success=False,
            reason_codes=["INVALID_NOMINAL_SPACING"],
            warnings=["Nominal spacing must be strictly positive."],
        )

    measurements: List[SpacingMeasurement] = []
    warnings: List[str] = []

    # 1. Horizontal gaps between adjacent vertical bars
    if len(vertical_bar_positions) >= 2:
        for idx in range(len(vertical_bar_positions) - 1):
            p1 = vertical_bar_positions[idx]
            p2 = vertical_bar_positions[idx + 1]
            gap_px = abs(p2 - p1)
            gap_mm = gap_px * scale_mm_per_pixel
            dev_mm = gap_mm - nominal_spacing_mm
            in_tol = abs(dev_mm) <= tolerance_mm

            # Quality heuristic based on extreme divergence from nominal
            rel_diff = abs(dev_mm) / nominal_spacing_mm
            quality = "high" if rel_diff < 0.10 else ("acceptable" if rel_diff < uncertainty_threshold_ratio else "uncertain")
            if quality == "uncertain":
                warnings.append(
                    f"Measurement H-{idx+1:02d} deviates significantly ({gap_mm:.1f} mm vs nominal {nominal_spacing_mm:.1f} mm)."
                )

            measurements.append(
                SpacingMeasurement(
                    measurement_id=f"H-{idx+1:02d}",
                    direction="horizontal_spacing",
                    bar_index_start=idx,
                    bar_index_end=idx + 1,
                    pixel_spacing=round(gap_px, 2),
                    spacing_mm=round(gap_mm, 2),
                    nominal_spacing_mm=round(nominal_spacing_mm, 2),
                    deviation_mm=round(dev_mm, 2),
                    tolerance_mm=round(tolerance_mm, 2),
                    in_tolerance=in_tol,
                    measurement_quality=quality,
                    evidence_region={
                        "axis": "x",
                        "start_px": round(p1, 2),
                        "end_px": round(p2, 2),
                    },
                )
            )

    # 2. Vertical gaps between adjacent horizontal bars
    if len(horizontal_bar_positions) >= 2:
        for idx in range(len(horizontal_bar_positions) - 1):
            p1 = horizontal_bar_positions[idx]
            p2 = horizontal_bar_positions[idx + 1]
            gap_px = abs(p2 - p1)
            gap_mm = gap_px * scale_mm_per_pixel
            dev_mm = gap_mm - nominal_spacing_mm
            in_tol = abs(dev_mm) <= tolerance_mm

            rel_diff = abs(dev_mm) / nominal_spacing_mm
            quality = "high" if rel_diff < 0.10 else ("acceptable" if rel_diff < uncertainty_threshold_ratio else "uncertain")
            if quality == "uncertain":
                warnings.append(
                    f"Measurement V-{idx+1:02d} deviates significantly ({gap_mm:.1f} mm vs nominal {nominal_spacing_mm:.1f} mm)."
                )

            measurements.append(
                SpacingMeasurement(
                    measurement_id=f"V-{idx+1:02d}",
                    direction="vertical_spacing",
                    bar_index_start=idx,
                    bar_index_end=idx + 1,
                    pixel_spacing=round(gap_px, 2),
                    spacing_mm=round(gap_mm, 2),
                    nominal_spacing_mm=round(nominal_spacing_mm, 2),
                    deviation_mm=round(dev_mm, 2),
                    tolerance_mm=round(tolerance_mm, 2),
                    in_tolerance=in_tol,
                    measurement_quality=quality,
                    evidence_region={
                        "axis": "y",
                        "start_px": round(p1, 2),
                        "end_px": round(p2, 2),
                    },
                )
            )

    if not measurements:
        return SpacingEvaluationResult(
            success=False,
            reason_codes=["NO_SPACINGS_MEASURABLE"],
            warnings=["Could not compute any adjacent bar spacing."],
        )

    # Summary statistics
    spacings = [m.spacing_mm for m in measurements]
    in_tol_count = sum(1 for m in measurements if m.in_tolerance)
    out_tol_count = len(measurements) - in_tol_count
    max_dev = max(abs(m.deviation_mm) for m in measurements)

    summary = MeasurementSummary(
        total_gaps_measured=len(measurements),
        in_tolerance_count=in_tol_count,
        out_of_tolerance_count=out_tol_count,
        all_in_tolerance=(out_tol_count == 0),
        mean_spacing_mm=round(float(np.mean(spacings)), 2),
        min_spacing_mm=round(float(np.min(spacings)), 2),
        max_spacing_mm=round(float(np.max(spacings)), 2),
        std_spacing_mm=round(float(np.std(spacings)), 2),
        max_abs_deviation_mm=round(float(max_dev), 2),
    )

    return SpacingEvaluationResult(
        success=True,
        measurements=measurements,
        summary=summary,
        warnings=warnings,
    )
