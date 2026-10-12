"""Image quality gates and validation for PourProof vision pipeline.

Evaluates blur, exposure, contrast, and resolution before attempting
calibration or measurement.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import cv2
import numpy as np


@dataclass
class QualityCheckResult:
    accepted: bool
    reason_codes: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


def evaluate_image_quality(
    image: np.ndarray,
    blur_threshold: float = 80.0,
    min_mean_luminance: float = 30.0,
    max_mean_luminance: float = 225.0,
    min_width: int = 400,
    min_height: int = 400,
) -> QualityCheckResult:
    """Evaluate image quality against documented thresholds.
    
    Args:
        image: Decoded image as a NumPy array (BGR or Grayscale).
        blur_threshold: Minimum Laplacian variance for acceptable sharpness.
        min_mean_luminance: Minimum average luminance (0-255).
        max_mean_luminance: Maximum average luminance (0-255).
        min_width: Minimum acceptable image width in pixels.
        min_height: Minimum acceptable image height in pixels.
        
    Returns:
        QualityCheckResult containing acceptance decision, metrics, and reason codes.
    """
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        return QualityCheckResult(
            accepted=False,
            reason_codes=["IMAGE_EMPTY_OR_UNREADABLE"],
            metrics={},
        )

    height, width = image.shape[:2]
    channels = image.shape[2] if image.ndim == 3 else 1
    
    # 1. Dimension check
    reason_codes = []
    if width < min_width or height < min_height:
        reason_codes.append("IMAGE_DIMENSIONS_TOO_SMALL")

    # Convert to grayscale for blur and luminance evaluation
    if channels == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif channels == 4:
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    else:
        gray = image

    # 2. Sharpness (Laplacian variance)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < blur_threshold:
        reason_codes.append("IMAGE_TOO_BLURRY")

    # 3. Luminance / Exposure
    mean_luminance = float(np.mean(gray))
    if mean_luminance < min_mean_luminance:
        reason_codes.append("IMAGE_UNDEREXPOSED")
    elif mean_luminance > max_mean_luminance:
        reason_codes.append("IMAGE_OVEREXPOSED")

    # 4. Dynamic range / contrast check (low contrast if standard deviation < 15)
    std_luminance = float(np.std(gray))
    if std_luminance < 15.0 and "IMAGE_UNDEREXPOSED" not in reason_codes and "IMAGE_OVEREXPOSED" not in reason_codes:
        reason_codes.append("IMAGE_LOW_CONTRAST")

    metrics = {
        "width": width,
        "height": height,
        "channels": channels,
        "blur_score": round(laplacian_var, 2),
        "blur_threshold": blur_threshold,
        "mean_luminance": round(mean_luminance, 2),
        "std_luminance": round(std_luminance, 2),
    }

    accepted = len(reason_codes) == 0
    return QualityCheckResult(
        accepted=accepted,
        reason_codes=reason_codes,
        metrics=metrics,
    )
