"""Calibration module using planar fiducial markers in OpenCV 5.

Establishes metric pixel-to-millimeter scale from a known-size planar marker
coplanar with the reinforcement grid.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any, Dict
import cv2
import numpy as np


@dataclass
class CalibrationResult:
    valid: bool
    method: str = "aruco_marker"
    scale_mm_per_pixel: Optional[float] = None
    pixels_per_mm: Optional[float] = None
    marker_id: Optional[int] = None
    marker_corners: Optional[List[List[float]]] = None
    marker_side_pixels: Optional[float] = None
    aspect_ratio_divergence: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)


def detect_calibration_marker(
    image: np.ndarray,
    marker_dimension_mm: float,
    dictionary_id: int = cv2.aruco.DICT_4X4_50,
    min_marker_pixel_area: float = 900.0,
    max_aspect_ratio_divergence: float = 0.40,
) -> CalibrationResult:
    """Detect known planar fiducial marker and calculate metric scale.
    
    Args:
        image: BGR or grayscale image as NumPy array.
        marker_dimension_mm: Known physical edge length of the square marker in mm.
        dictionary_id: OpenCV ArUco dictionary ID (default DICT_4X4_50).
        min_marker_pixel_area: Minimum pixel area required to consider marker valid.
        max_aspect_ratio_divergence: Maximum allowed divergence between side lengths
            before flagging high perspective distortion.
            
    Returns:
        CalibrationResult with scale, corners, and validity flags.
    """
    if marker_dimension_mm <= 0:
        return CalibrationResult(
            valid=False,
            reason_codes=["INVALID_MARKER_DIMENSION"],
            warnings=["Calibration marker dimension must be positive."],
        )

    # Convert to grayscale if necessary
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Initialize OpenCV 5 ArucoDetector with subpixel corner refinement
    aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary_id)
    detector_params = cv2.aruco.DetectorParameters()
    detector_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
    detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)

    corners_list, ids, _ = detector.detectMarkers(gray)

    if ids is None or len(corners_list) == 0:
        return CalibrationResult(
            valid=False,
            reason_codes=["CALIBRATION_MARKER_NOT_FOUND"],
            warnings=["No fiducial marker detected in the image."],
        )

    # Choose the first detected marker (or largest if multiple)
    best_idx = 0
    if len(corners_list) > 1:
        # Pick marker with highest area
        areas = [cv2.contourArea(c[0]) for c in corners_list]
        best_idx = int(np.argmax(areas))

    marker_id = int(np.asarray(ids[best_idx]).flatten()[0])
    pts = corners_list[best_idx][0]  # shape (4, 2)
    area = float(cv2.contourArea(pts))

    if area < min_marker_pixel_area:
        return CalibrationResult(
            valid=False,
            marker_id=marker_id,
            reason_codes=["MARKER_TOO_SMALL_IN_FRAME"],
            warnings=[f"Marker area {area:.1f} px² is below minimum {min_marker_pixel_area} px²."],
        )

    # Calculate side lengths: [top, right, bottom, left]
    # pts order: 0=TL, 1=TR, 2=BR, 3=BL
    s0 = float(np.linalg.norm(pts[1] - pts[0]))  # Top
    s1 = float(np.linalg.norm(pts[2] - pts[1]))  # Right
    s2 = float(np.linalg.norm(pts[3] - pts[2]))  # Bottom
    s3 = float(np.linalg.norm(pts[0] - pts[3]))  # Left
    side_lengths = [s0, s1, s2, s3]
    avg_side_px = float(np.mean(side_lengths))

    max_side = max(side_lengths)
    min_side = min(side_lengths)
    aspect_divergence = (max_side - min_side) / avg_side_px

    warnings = []
    if aspect_divergence > max_aspect_ratio_divergence:
        warnings.append(
            f"Foreshortening detected on calibration marker (divergence: {aspect_divergence:.2f}). "
            "Planar rectification recommended."
        )

    # Calculate scale: mm per pixel
    scale_mm_per_px = marker_dimension_mm / avg_side_px
    px_per_mm = avg_side_px / marker_dimension_mm

    if px_per_mm < 1.0:
        warnings.append(
            f"Low spatial resolution ({px_per_mm:.2f} px/mm). Spacing measurement uncertainty is elevated."
        )

    corners_serializable = [[float(p[0]), float(p[1])] for p in pts]

    return CalibrationResult(
        valid=True,
        method="aruco_marker",
        scale_mm_per_pixel=round(scale_mm_per_px, 5),
        pixels_per_mm=round(px_per_mm, 3),
        marker_id=marker_id,
        marker_corners=corners_serializable,
        marker_side_pixels=round(avg_side_px, 2),
        aspect_ratio_divergence=round(aspect_divergence, 3),
        warnings=warnings,
    )
