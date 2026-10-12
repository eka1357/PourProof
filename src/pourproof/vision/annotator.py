"""Annotation overlay generator adhering to PourProof UI/UX specifications.

Generates engineering-grade visual evidence overlays with restrained,
high-contrast technical graphics.
"""

from typing import List, Optional, Any, Dict
import cv2
import numpy as np
from pourproof.vision.measurement import SpacingMeasurement


# Color tokens (BGR format for OpenCV)
COLOR_PRIMARY_TEAL = (193, 217, 101)  # #65d9c1 in BGR
COLOR_WARNING_AMBER = (105, 191, 243) # #f3bf69 in BGR
COLOR_DANGER_RED = (119, 119, 255)    # #ff7777 in BGR
COLOR_NEUTRAL_SLATE = (184, 175, 160) # #a0afb8 in BGR
COLOR_DARK_SURFACE = (33, 26, 17)     # #111a21 in BGR
COLOR_TEXT_LIGHT = (245, 243, 237)    # #edf3f5 in BGR


def draw_inspection_annotations(
    image: np.ndarray,
    measurements: List[SpacingMeasurement],
    vertical_positions: List[float],
    horizontal_positions: List[float],
    marker_corners: Optional[List[List[float]]] = None,
    marker_id: Optional[int] = None,
    inspection_status: str = "measured",
) -> np.ndarray:
    """Render high-contrast, technical inspection overlays on the evidence image.
    
    Args:
        image: Original or rectified BGR image.
        measurements: Computed SpacingMeasurement list.
        vertical_positions: X-coordinates of vertical bar centerlines.
        horizontal_positions: Y-coordinates of horizontal bar centerlines.
        marker_corners: Optional 4-corner coordinates of fiducial marker.
        marker_id: Optional detected ArUco marker ID.
        inspection_status: High-level status string for status badge.
        
    Returns:
        New BGR NumPy array containing the rendered annotation layer.
    """
    canvas = image.copy()
    h, w = canvas.shape[:2]

    # 1. Draw detected bar centerlines
    # Vertical bars
    for x in vertical_positions:
        ix = int(round(x))
        if 0 <= ix < w:
            cv2.line(canvas, (ix, 0), (ix, h), COLOR_PRIMARY_TEAL, 1, cv2.LINE_AA)

    # Horizontal bars
    for y in horizontal_positions:
        iy = int(round(y))
        if 0 <= iy < h:
            cv2.line(canvas, (0, iy), (w, iy), COLOR_PRIMARY_TEAL, 1, cv2.LINE_AA)

    # 2. Draw calibration marker polygon if available
    if marker_corners and len(marker_corners) == 4:
        poly_pts = np.array(marker_corners, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(canvas, [poly_pts], isClosed=True, color=COLOR_PRIMARY_TEAL, thickness=2, lineType=cv2.LINE_AA)
        
        # Draw label
        top_left = (int(marker_corners[0][0]), int(marker_corners[0][1]))
        label = f"REF MARKER ID:{marker_id}" if marker_id is not None else "CALIBRATION REF"
        cv2.putText(
            canvas,
            label,
            (top_left[0], max(15, top_left[1] - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            COLOR_PRIMARY_TEAL,
            1,
            cv2.LINE_AA,
        )

    # 3. Draw spacing dimensions and labels
    # Horizontal spacing (between vertical bars)
    for m in measurements:
        is_horiz = m.direction == "horizontal_spacing"
        is_tol = m.in_tolerance
        color = COLOR_PRIMARY_TEAL if is_tol else COLOR_WARNING_AMBER

        if is_horiz:
            x1 = int(round(m.evidence_region["start_px"]))
            x2 = int(round(m.evidence_region["end_px"]))
            # Position dimension line in upper third
            y_dim = int(h * 0.25)
            # Dimension line with end ticks
            cv2.line(canvas, (x1, y_dim), (x2, y_dim), color, 2, cv2.LINE_AA)
            cv2.line(canvas, (x1, y_dim - 6), (x1, y_dim + 6), color, 2, cv2.LINE_AA)
            cv2.line(canvas, (x2, y_dim - 6), (x2, y_dim + 6), color, 2, cv2.LINE_AA)

            text = f"{m.spacing_mm:.1f} mm"
            if not is_tol:
                text += f" (d:{m.deviation_mm:+.1f})"
            mid_x = (x1 + x2) // 2
            cv2.putText(
                canvas,
                text,
                (max(10, mid_x - 35), y_dim - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.40,
                color,
                1,
                cv2.LINE_AA,
            )
        else:
            # Vertical spacing (between horizontal bars)
            y1 = int(round(m.evidence_region["start_px"]))
            y2 = int(round(m.evidence_region["end_px"]))
            x_dim = int(w * 0.75)
            cv2.line(canvas, (x_dim, y1), (x_dim, y2), color, 2, cv2.LINE_AA)
            cv2.line(canvas, (x_dim - 6, y1), (x_dim + 6, y1), color, 2, cv2.LINE_AA)
            cv2.line(canvas, (x_dim - 6, y2), (x_dim + 6, y2), color, 2, cv2.LINE_AA)

            text = f"{m.spacing_mm:.1f} mm"
            if not is_tol:
                text += f" (d:{m.deviation_mm:+.1f})"
            mid_y = (y1 + y2) // 2
            cv2.putText(
                canvas,
                text,
                (min(w - 110, x_dim + 10), mid_y + 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.40,
                color,
                1,
                cv2.LINE_AA,
            )

    # 4. Status badge banner in top-left
    badge_color = COLOR_PRIMARY_TEAL if inspection_status == "measured" else (
        COLOR_WARNING_AMBER if inspection_status in ("needs_review", "needs_recapture") else COLOR_DANGER_RED
    )
    badge_text = f"POURPROOF: {inspection_status.upper()}"
    cv2.rectangle(canvas, (10, 10), (220, 36), COLOR_DARK_SURFACE, -1)
    cv2.rectangle(canvas, (10, 10), (220, 36), badge_color, 1)
    cv2.putText(canvas, badge_text, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXT_LIGHT, 1, cv2.LINE_AA)

    return canvas
