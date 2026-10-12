"""Tests for OpenCV 5 runtime verification."""

import pytest
from pourproof.vision.runtime import verify_opencv5_runtime, get_opencv_runtime_info


def test_runtime_reports_opencv5():
    """Verify runtime diagnostics confirms OpenCV 5.x."""
    info = get_opencv_runtime_info()
    assert info["is_opencv5"] is True
    assert info["major_version"] == 5
    assert info["version"].startswith("5.")
    assert info["has_aruco"] is True
    assert "cv2" in info["module_path"]


def test_verify_opencv5_runtime_succeeds():
    """Verify assertion function succeeds on OpenCV 5 environment."""
    info = verify_opencv5_runtime()
    assert info["is_opencv5"] is True
