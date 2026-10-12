"""Rebar grid centerline detection module using OpenCV 5.

Detects candidate horizontal and vertical reinforcement bars from exposed mats.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import cv2
import numpy as np


@dataclass
class BarCandidate:
    axis: str  # "vertical" (varying x) or "horizontal" (varying y)
    centerline_coord: float  # x for vertical, y for horizontal
    segment_count: int
    total_length: float
    segments: List[List[int]] = field(default_factory=list)  # [[x1, y1, x2, y2], ...]


@dataclass
class GridDetectionResult:
    success: bool
    vertical_bars: List[BarCandidate] = field(default_factory=list)
    horizontal_bars: List[BarCandidate] = field(default_factory=list)
    vertical_positions: List[float] = field(default_factory=list)
    horizontal_positions: List[float] = field(default_factory=list)
    detected_line_count: int = 0
    reason_codes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def detect_rebar_grid(
    image: np.ndarray,
    min_line_length_ratio: float = 0.15,
    max_line_gap_ratio: float = 0.10,
    bar_merge_distance_px: float = 45.0,
    min_segments_per_bar: int = 1,
    min_bar_total_length_ratio: float = 0.20,
) -> GridDetectionResult:
    """Detect candidate rebar centerlines in horizontal and vertical directions.
    
    Args:
        image: BGR or grayscale image of planar or rectified rebar mat.
        min_line_length_ratio: Minimum line length as a fraction of image dimension.
        max_line_gap_ratio: Maximum gap between collinear segments as fraction of image dimension.
        bar_merge_distance_px: Pixel distance within which parallel segments belong to same bar.
        min_segments_per_bar: Minimum segments required to consider a bar valid.
        min_bar_total_length_ratio: Minimum cumulative length of a bar candidate.
        
    Returns:
        GridDetectionResult with detected bar candidates for both grid directions.
    """
    if image is None or image.size == 0:
        return GridDetectionResult(
            success=False,
            reason_codes=["IMAGE_EMPTY_OR_UNREADABLE"],
        )

    h, w = image.shape[:2]
    min_dim = min(h, w)
    min_line_length = max(30, int(min_dim * min_line_length_ratio))
    max_line_gap = max(10, int(min_dim * max_line_gap_ratio))
    min_total_length = max(40.0, float(min_dim * min_bar_total_length_ratio))

    # Preprocessing
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Bilateral filter suppresses surface noise while preserving prominent edges
    blurred = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

    # Adaptive Canny edge detection
    high_thresh, _ = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    low_thresh = 0.5 * high_thresh
    edges = cv2.Canny(blurred, int(low_thresh), int(high_thresh))

    # Hough Lines Probabilistic in OpenCV 5
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=35,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap,
    )

    if lines is None or len(lines) == 0:
        return GridDetectionResult(
            success=False,
            reason_codes=["INSUFFICIENT_GRID_BARS_DETECTED"],
            warnings=["No prominent line segments detected in image."],
        )

    vert_segments: List[Tuple[float, float, List[int]]] = []  # (x_center, length, [x1,y1,x2,y2])
    horiz_segments: List[Tuple[float, float, List[int]]] = [] # (y_center, length, [x1,y1,x2,y2])

    for line in lines:
        coords = np.asarray(line).flatten()
        x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
        dx = float(x2 - x1)
        dy = float(y2 - y1)
        length = float(np.hypot(dx, dy))
        if length < 1.0:
            continue

        angle_deg = np.degrees(np.arctan2(abs(dy), abs(dx)))

        border_margin_px = 15.0
        # Vertical bars: angle near 90 deg (75 to 90)
        if 75.0 <= angle_deg <= 90.0:
            x_mid = (x1 + x2) / 2.0
            if border_margin_px <= x_mid <= (w - border_margin_px):
                vert_segments.append((x_mid, length, [int(x1), int(y1), int(x2), int(y2)]))
        # Horizontal bars: angle near 0 deg (0 to 15)
        elif angle_deg <= 15.0:
            y_mid = (y1 + y2) / 2.0
            if border_margin_px <= y_mid <= (h - border_margin_px):
                horiz_segments.append((y_mid, length, [int(x1), int(y1), int(x2), int(y2)]))

    # Cluster segments into discrete bars
    def _cluster_bars(
        segments: List[Tuple[float, float, List[int]]],
        axis_name: str,
    ) -> List[BarCandidate]:
        if not segments:
            return []
        
        # Sort by coordinate
        segments.sort(key=lambda s: s[0])
        clusters: List[List[Tuple[float, float, List[int]]]] = []
        
        for seg in segments:
            coord, length, geom = seg
            if not clusters:
                clusters.append([seg])
            else:
                # Compare to current cluster mean
                cluster_coords = [s[0] for s in clusters[-1]]
                if abs(coord - np.mean(cluster_coords)) <= bar_merge_distance_px:
                    clusters[-1].append(seg)
                else:
                    clusters.append([seg])

        candidates = []
        for cluster in clusters:
            tot_len = sum(s[1] for s in cluster)
            # Weighted average coordinate based on segment length
            weighted_coord = float(sum(s[0] * s[1] for s in cluster) / tot_len)
            geoms = [s[2] for s in cluster]
            
            if len(cluster) >= min_segments_per_bar and tot_len >= min_total_length:
                candidates.append(
                    BarCandidate(
                        axis=axis_name,
                        centerline_coord=round(weighted_coord, 2),
                        segment_count=len(cluster),
                        total_length=round(tot_len, 2),
                        segments=geoms,
                    )
                )

        # Sort candidates strictly by coordinate
        candidates.sort(key=lambda c: c.centerline_coord)
        return candidates

    vert_bars = _cluster_bars(vert_segments, "vertical")
    horiz_bars = _cluster_bars(horiz_segments, "horizontal")

    vert_positions = [b.centerline_coord for b in vert_bars]
    horiz_positions = [b.centerline_coord for b in horiz_bars]

    reason_codes = []
    warnings = []

    # Valid grid requires at least 2 adjacent bars in at least one primary direction
    has_sufficient_bars = len(vert_bars) >= 2 or len(horiz_bars) >= 2
    if not has_sufficient_bars:
        reason_codes.append("INSUFFICIENT_GRID_BARS_DETECTED")
        warnings.append(
            f"Detected {len(vert_bars)} vertical and {len(horiz_bars)} horizontal bars. "
            "At least 2 parallel bars in one direction are required to measure spacing."
        )

    return GridDetectionResult(
        success=has_sufficient_bars,
        vertical_bars=vert_bars,
        horizontal_bars=horiz_bars,
        vertical_positions=vert_positions,
        horizontal_positions=horiz_positions,
        detected_line_count=len(lines),
        reason_codes=reason_codes,
        warnings=warnings,
    )
