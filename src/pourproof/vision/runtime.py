"""Runtime verification for OpenCV 5.

PourProof requires OpenCV 5 substantively. This module checks runtime cv2
version and path, failing explicitly if OpenCV 5 is not active.
"""

from typing import Any, Dict
import cv2


def get_opencv_runtime_info() -> Dict[str, Any]:
    """Retrieve verified OpenCV runtime diagnostics."""
    version_str = getattr(cv2, "__version__", "unknown")
    module_path = getattr(cv2, "__file__", "unknown")
    
    version_parts = version_str.split(".")
    major_version = int(version_parts[0]) if version_parts[0].isdigit() else -1
    is_opencv5 = major_version == 5

    return {
        "version": version_str,
        "major_version": major_version,
        "is_opencv5": is_opencv5,
        "module_path": module_path,
        "has_aruco": hasattr(cv2, "aruco") and hasattr(cv2.aruco, "ArucoDetector"),
    }


def verify_opencv5_runtime() -> Dict[str, Any]:
    """Assert that OpenCV 5 is active and return runtime diagnostics.
    
    Raises:
        RuntimeError: If cv2 version is not OpenCV 5.x.
    """
    info = get_opencv_runtime_info()
    if not info["is_opencv5"]:
        raise RuntimeError(
            f"OpenCV 5 requirement failed. Installed version is '{info['version']}' "
            f"at '{info['module_path']}'. PourProof requires OpenCV 5.x and does not fall back to OpenCV 4."
        )
    return info
