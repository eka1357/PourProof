"""Planar perspective rectification module using OpenCV 5.

Removes oblique camera perspective distortion based on coplanar fiducial marker geometry.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Any
import cv2
import numpy as np


@dataclass
class RectificationResult:
    success: bool
    rectified_image: Optional[np.ndarray] = None
    rectified_scale_mm_per_pixel: Optional[float] = None
    homography_matrix: Optional[List[List[float]]] = None
    reason_codes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def rectify_planar_view(
    image: np.ndarray,
    marker_corners: List[List[float]],
    marker_dimension_mm: float,
    max_expansion_ratio: float = 3.5,
) -> RectificationResult:
    """Rectify an oblique photograph to an orthogonal top-down metric plane.
    
    Args:
        image: Original BGR or grayscale image.
        marker_corners: 4 detected marker corner points [[x, y], ...].
        marker_dimension_mm: Physical dimension of marker side in mm.
        max_expansion_ratio: Maximum allowed expansion factor for warped canvas.
        
    Returns:
        RectificationResult with warped image, metric scale, and homography.
    """
    if len(marker_corners) != 4:
        return RectificationResult(
            success=False,
            reason_codes=["INVALID_MARKER_GEOMETRY"],
            warnings=["Exactly 4 marker corners are required for rectification."],
        )

    h_orig, w_orig = image.shape[:2]
    src_pts = np.array(marker_corners, dtype=np.float32)

    # Compute average side length in pixels to determine canonical scale
    s0 = float(np.linalg.norm(src_pts[1] - src_pts[0]))
    s1 = float(np.linalg.norm(src_pts[2] - src_pts[1]))
    s2 = float(np.linalg.norm(src_pts[3] - src_pts[2]))
    s3 = float(np.linalg.norm(src_pts[0] - src_pts[3]))
    canonical_side_px = float(np.mean([s0, s1, s2, s3]))

    if canonical_side_px <= 1.0:
        return RectificationResult(
            success=False,
            reason_codes=["MARKER_DEGENERATE"],
            warnings=["Marker pixel dimensions are too small or degenerate."],
        )

    # Canonical square corners: TL, TR, BR, BL
    dst_pts = np.array([
        [0.0, 0.0],
        [canonical_side_px, 0.0],
        [canonical_side_px, canonical_side_px],
        [0.0, canonical_side_px],
    ], dtype=np.float32)

    try:
        H_marker = cv2.getPerspectiveTransform(src_pts, dst_pts)
    except cv2.error as e:
        return RectificationResult(
            success=False,
            reason_codes=["HOMOGRAPHY_ESTIMATION_FAILED"],
            warnings=[str(e)],
        )

    # Transform 4 image corners to determine global rectified bounds
    img_corners = np.array([
        [0.0, 0.0],
        [float(w_orig), 0.0],
        [float(w_orig), float(h_orig)],
        [0.0, float(h_orig)],
    ], dtype=np.float32).reshape(-1, 1, 2)

    warped_corners = cv2.perspectiveTransform(img_corners, H_marker)
    if warped_corners is None:
        return RectificationResult(
            success=False,
            reason_codes=["PERSPECTIVE_WARP_FAILED"],
            warnings=["Failed to project image bounds through homography."],
        )

    pts_warped = warped_corners.reshape(-1, 2)
    x_min, y_min = np.min(pts_warped, axis=0)
    x_max, y_max = np.max(pts_warped, axis=0)

    rect_w = int(np.ceil(x_max - x_min))
    rect_h = int(np.ceil(y_max - y_min))

    # Guard against extreme oblique angles causing massive memory allocations
    if rect_w > w_orig * max_expansion_ratio or rect_h > h_orig * max_expansion_ratio or rect_w <= 0 or rect_h <= 0:
        return RectificationResult(
            success=False,
            reason_codes=["PERSPECTIVE_DISTORTION_TOO_HIGH"],
            warnings=[
                f"Camera perspective angle is too oblique (rectified canvas would be {rect_w}x{rect_h} px). "
                "Retake photograph closer to normal incidence."
            ],
        )

    # Translation matrix to align origin
    T = np.array([
        [1.0, 0.0, -x_min],
        [0.0, 1.0, -y_min],
        [0.0, 0.0, 1.0],
    ], dtype=np.float64)

    H_final = T @ H_marker

    try:
        rectified = cv2.warpPerspective(
            image,
            H_final,
            (rect_w, rect_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )
    except cv2.error as e:
        return RectificationResult(
            success=False,
            reason_codes=["WARP_PERSPECTIVE_ERROR"],
            warnings=[str(e)],
        )

    scale_mm_per_px = marker_dimension_mm / canonical_side_px

    return RectificationResult(
        success=True,
        rectified_image=rectified,
        rectified_scale_mm_per_pixel=round(scale_mm_per_px, 5),
        homography_matrix=H_final.tolist(),
        warnings=[],
    )
