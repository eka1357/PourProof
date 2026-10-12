"""Tests for image quality evaluation and gating."""

import numpy as np
import pytest
from pourproof.vision.quality import evaluate_image_quality
from tests.fixtures.synthetic_generator import (
    generate_synthetic_rebar_grid,
    generate_blurry_fixture,
    generate_underexposed_fixture,
    generate_overexposed_fixture,
)


def test_clean_fixture_passes_quality_gate():
    """Verify sharp, well-exposed synthetic image passes quality checks."""
    img, _ = generate_synthetic_rebar_grid()
    result = evaluate_image_quality(img)
    assert result.accepted is True
    assert len(result.reason_codes) == 0
    assert result.metrics["blur_score"] > 80.0


def test_blurry_fixture_rejected():
    """Verify blurry image is cleanly rejected with IMAGE_TOO_BLURRY."""
    img, _ = generate_blurry_fixture()
    result = evaluate_image_quality(img)
    assert result.accepted is False
    assert "IMAGE_TOO_BLURRY" in result.reason_codes


def test_underexposed_fixture_rejected():
    """Verify dark image is rejected with IMAGE_UNDEREXPOSED."""
    img, _ = generate_underexposed_fixture()
    result = evaluate_image_quality(img)
    assert result.accepted is False
    assert "IMAGE_UNDEREXPOSED" in result.reason_codes


def test_overexposed_fixture_rejected():
    """Verify washed-out image is rejected with IMAGE_OVEREXPOSED."""
    img, _ = generate_overexposed_fixture()
    result = evaluate_image_quality(img)
    assert result.accepted is False
    assert "IMAGE_OVEREXPOSED" in result.reason_codes


def test_undersized_image_rejected():
    """Verify image smaller than minimum required dimensions is rejected."""
    tiny_img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = evaluate_image_quality(tiny_img)
    assert result.accepted is False
    assert "IMAGE_DIMENSIONS_TOO_SMALL" in result.reason_codes


def test_empty_image_rejected():
    """Verify empty or None image is safely rejected without crashing."""
    result = evaluate_image_quality(None)  # type: ignore
    assert result.accepted is False
    assert "IMAGE_EMPTY_OR_UNREADABLE" in result.reason_codes
