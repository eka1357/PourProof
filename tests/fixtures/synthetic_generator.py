"""Deterministic synthetic rebar inspection fixture generator.

Creates synthetic planar rebar images with mathematically exact ground truth
dimensions and negative test cases for vision pipeline verification.

NOTE: All outputs from this module are synthetic and labeled as such.
They verify algorithmic correctness and cannot be represented as field validation.
"""

from typing import Dict, Any, Tuple
import cv2
import numpy as np


def generate_synthetic_rebar_grid(
    canvas_size: int = 900,
    scale_mm_per_px: float = 0.50,
    nominal_spacing_mm: float = 150.0,
    marker_dimension_mm: float = 50.0,
    bar_thickness_mm: float = 16.0,
    include_marker: bool = True,
    irregular_spacing_mm: float = 0.0,
    seed: int = 42,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate a clean, calibrated synthetic planar rebar grid image with exact ground truth.
    
    Args:
        canvas_size: Square canvas dimension in pixels.
        scale_mm_per_px: Synthetic scale factor (mm per pixel).
        nominal_spacing_mm: Spacing between bars in mm.
        marker_dimension_mm: Dimension of calibration marker in mm.
        bar_thickness_mm: Diameter of simulated rebar in mm.
        include_marker: Whether to render the ArUco fiducial marker.
        irregular_spacing_mm: Offset to add to the second gap to simulate out-of-tolerance.
        seed: Random seed for deterministic reproducibility.
        
    Returns:
        Tuple of (BGR synthetic image array, ground truth metadata dictionary).
    """
    rng = np.random.RandomState(seed)

    # 1. Base simulated concrete canvas (gray with slight texture)
    base_color = 145
    noise = rng.normal(0, 4, (canvas_size, canvas_size)).astype(np.float32)
    canvas = np.clip(base_color + noise, 0, 255).astype(np.uint8)
    canvas_bgr = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

    spacing_px = int(round(nominal_spacing_mm / scale_mm_per_px))
    bar_thickness_px = max(8, int(round(bar_thickness_mm / scale_mm_per_px)))
    marker_px = int(round(marker_dimension_mm / scale_mm_per_px))

    # Grid bar centerline coordinates (3 bars in each direction)
    start_offset = 200
    irregular_px = int(round(irregular_spacing_mm / scale_mm_per_px))
    x_positions = [
        start_offset,
        start_offset + spacing_px + irregular_px,
        start_offset + spacing_px * 2,
    ]
    y_positions = [
        start_offset,
        start_offset + spacing_px,
        start_offset + spacing_px * 2,
    ]

    bar_color = (45, 45, 50)         # Dark steel
    highlight_color = (80, 80, 85)   # Specular highlight

    # 2. Draw horizontal bars
    for y in y_positions:
        top_y = y - bar_thickness_px // 2
        bot_y = y + bar_thickness_px // 2
        cv2.rectangle(canvas_bgr, (0, top_y), (canvas_size, bot_y), bar_color, -1)
        # Highlight center stripe
        cv2.line(canvas_bgr, (0, y), (canvas_size, y), highlight_color, 2)

    # 3. Draw vertical bars
    for x in x_positions:
        left_x = x - bar_thickness_px // 2
        right_x = x + bar_thickness_px // 2
        cv2.rectangle(canvas_bgr, (left_x, 0), (right_x, canvas_size), bar_color, -1)
        cv2.line(canvas_bgr, (x, 0), (x, canvas_size), highlight_color, 2)

    # 4. Draw ArUco fiducial marker in top-left corner
    marker_pos = (30, 30)
    if include_marker:
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        marker_img = cv2.aruco.generateImageMarker(aruco_dict, id=0, sidePixels=marker_px)
        marker_bgr = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
        
        # White border backing for high contrast on concrete
        pad = 10
        cv2.rectangle(
            canvas_bgr,
            (marker_pos[0] - pad, marker_pos[1] - pad),
            (marker_pos[0] + marker_px + pad, marker_pos[1] + marker_px + pad),
            (240, 240, 240),
            -1,
        )
        canvas_bgr[
            marker_pos[1] : marker_pos[1] + marker_px,
            marker_pos[0] : marker_pos[0] + marker_px,
        ] = marker_bgr

    # Compute exact ground truth spacings
    gt_horizontal_spacings_mm = [
        (x_positions[i + 1] - x_positions[i]) * scale_mm_per_px
        for i in range(len(x_positions) - 1)
    ]
    gt_vertical_spacings_mm = [
        (y_positions[i + 1] - y_positions[i]) * scale_mm_per_px
        for i in range(len(y_positions) - 1)
    ]

    ground_truth = {
        "is_synthetic": True,
        "provenance": "synthetic_mathematical_generator",
        "canvas_size": canvas_size,
        "scale_mm_per_px": scale_mm_per_px,
        "nominal_spacing_mm": nominal_spacing_mm,
        "marker_dimension_mm": marker_dimension_mm,
        "marker_present": include_marker,
        "vertical_bar_positions_px": x_positions,
        "horizontal_bar_positions_px": y_positions,
        "ground_truth_horizontal_spacings_mm": gt_horizontal_spacings_mm,
        "ground_truth_vertical_spacings_mm": gt_vertical_spacings_mm,
    }

    return canvas_bgr, ground_truth


def generate_blurry_fixture() -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate an intentionally blurred fixture (negative test for sharpness gate)."""
    clean_img, meta = generate_synthetic_rebar_grid()
    blurry = cv2.GaussianBlur(clean_img, (35, 35), sigmaX=15)
    meta["defect"] = "blur"
    return blurry, meta


def generate_underexposed_fixture() -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate an intentionally underexposed fixture (negative test for exposure gate)."""
    clean_img, meta = generate_synthetic_rebar_grid()
    dark = (clean_img.astype(np.float32) * 0.08).astype(np.uint8)
    meta["defect"] = "underexposed"
    return dark, meta


def generate_overexposed_fixture() -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate an intentionally overexposed fixture (negative test for exposure gate)."""
    clean_img, meta = generate_synthetic_rebar_grid()
    bright = np.clip(clean_img.astype(np.int32) + 215, 0, 255).astype(np.uint8)
    meta["defect"] = "overexposed"
    return bright, meta


def generate_missing_marker_fixture() -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate a rebar fixture without any calibration marker (negative test for calibration)."""
    img, meta = generate_synthetic_rebar_grid(include_marker=False)
    meta["defect"] = "missing_marker"
    return img, meta


def generate_perspective_skewed_fixture() -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate an oblique/skewed fixture with extreme perspective distortion."""
    clean_img, meta = generate_synthetic_rebar_grid()
    h, w = clean_img.shape[:2]
    
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    # Severe perspective tilt
    dst = np.array([[w * 0.35, h * 0.1], [w * 0.65, h * 0.1], [w * 0.95, h * 0.9], [w * 0.05, h * 0.9]], dtype=np.float32)
    
    M = cv2.getPerspectiveTransform(src, dst)
    skewed = cv2.warpPerspective(clean_img, M, (w, h), borderValue=(0, 0, 0))
    meta["defect"] = "extreme_perspective_skew"
    return skewed, meta
