"""FastAPI integration and endpoint tests using synthetic fixtures."""

import io
import cv2
import pytest
from fastapi.testclient import TestClient

from pourproof.api.app import app
from tests.fixtures.synthetic_generator import (
    generate_synthetic_rebar_grid,
    generate_blurry_fixture,
    generate_missing_marker_fixture,
)

client = TestClient(app)


def _encode_to_png_bytes(img) -> bytes:
    """Encode OpenCV BGR array to PNG byte stream."""
    success, buf = cv2.imencode(".png", img)
    assert success, "Failed to encode image to PNG"
    return buf.tobytes()


def test_api_health_endpoint():
    """Verify GET /api/health reports verified OpenCV 5 runtime."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "pourproof-api"
    assert data["opencv_version"].startswith("5.")


def test_api_measure_valid_synthetic_fixture():
    """Verify POST /api/v1/measure succeeds on clean fixture with full schema."""
    img, _ = generate_synthetic_rebar_grid(
        nominal_spacing_mm=150.0,
        marker_dimension_mm=50.0,
    )
    png_bytes = _encode_to_png_bytes(img)

    response = client.post(
        "/api/v1/measure",
        files={"image": ("rebar_mat.png", png_bytes, "image/png")},
        data={
            "nominal_spacing_mm": "150.0",
            "tolerance_mm": "15.0",
            "calibration_marker_mm": "50.0",
            "session_id": "session-test-01",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Schema verification
    assert data["schema_version"] == "1.0"
    assert "inspection_id" in data
    assert "trace_id" in data
    assert data["status"] == "measured"
    assert data["next_action"]["action"] == "DONE"
    assert data["quality_gate"]["accepted"] is True
    assert data["calibration"]["valid"] is True
    assert data["calibration"]["scale_mm_per_pixel"] == 0.5

    # Measurement separation
    assert len(data["measurements"]) >= 2
    for m in data["measurements"]:
        assert m["nominal_spacing_mm"] == 150.0
        assert abs(m["spacing_mm"] - 150.0) < 0.20
        assert abs(m["deviation_mm"]) < 0.20
        assert m["in_tolerance"] is True

    # Annotated image endpoint verification
    annotated_url = data["annotated_image_url"]
    assert annotated_url is not None
    img_resp = client.get(annotated_url)
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] == "image/png"
    assert len(img_resp.content) > 1000


def test_api_measure_out_of_tolerance():
    """Verify POST /api/v1/measure accurately reports out-of-tolerance spacing as needs_review."""
    img, _ = generate_synthetic_rebar_grid(
        nominal_spacing_mm=150.0,
        irregular_spacing_mm=35.0,  # 185mm & 115mm gaps
    )
    png_bytes = _encode_to_png_bytes(img)

    response = client.post(
        "/api/v1/measure",
        files={"image": ("rebar_out_of_tol.png", png_bytes, "image/png")},
        data={
            "nominal_spacing_mm": "150.0",
            "tolerance_mm": "10.0",
            "calibration_marker_mm": "50.0",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "needs_review"
    assert data["next_action"]["action"] == "REVIEW_MEASUREMENT"
    assert data["next_action"]["reason_code"] == "SPACING_OUT_OF_TOLERANCE"
    assert data["summary"]["all_in_tolerance"] is False
    assert data["summary"]["out_of_tolerance_count"] >= 1


def test_api_measure_blurry_fixture_abstains():
    """Verify blurry photo triggers needs_recapture with 0 measurements."""
    img, _ = generate_blurry_fixture()
    png_bytes = _encode_to_png_bytes(img)

    response = client.post(
        "/api/v1/measure",
        files={"image": ("blurry_mat.png", png_bytes, "image/png")},
        data={
            "nominal_spacing_mm": "150.0",
            "tolerance_mm": "15.0",
            "calibration_marker_mm": "50.0",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "needs_recapture"
    assert data["next_action"]["action"] == "REQUEST_RECAPTURE"
    assert data["next_action"]["reason_code"] == "IMAGE_TOO_BLURRY"
    assert data["quality_gate"]["accepted"] is False
    assert len(data["measurements"]) == 0


def test_api_measure_missing_marker_abstains():
    """Verify uncalibrated photo triggers needs_recapture with 0 measurements."""
    img, _ = generate_missing_marker_fixture()
    png_bytes = _encode_to_png_bytes(img)

    response = client.post(
        "/api/v1/measure",
        files={"image": ("no_marker.png", png_bytes, "image/png")},
        data={
            "nominal_spacing_mm": "150.0",
            "tolerance_mm": "15.0",
            "calibration_marker_mm": "50.0",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "needs_recapture"
    assert data["next_action"]["action"] == "REQUEST_RECAPTURE"
    assert data["next_action"]["reason_code"] == "CALIBRATION_MARKER_NOT_FOUND"
    assert data["calibration"]["valid"] is False
    assert len(data["measurements"]) == 0


def test_api_measure_corrupted_image_rejected():
    """Verify corrupted non-image bytes safely returns rejected_input without server crash."""
    corrupt_bytes = b"NOT_A_VALID_IMAGE_HEADER_1234567890"

    response = client.post(
        "/api/v1/measure",
        files={"image": ("corrupted.png", corrupt_bytes, "image/png")},
        data={
            "nominal_spacing_mm": "150.0",
            "tolerance_mm": "15.0",
            "calibration_marker_mm": "50.0",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected_input"
    assert data["next_action"]["action"] == "REQUEST_RECAPTURE"
    assert data["next_action"]["reason_code"] == "IMAGE_DECODE_FAILED"
    assert len(data["measurements"]) == 0


def test_api_measure_invalid_parameters():
    """Verify negative or non-positive parameters are rejected with HTTP 422."""
    img, _ = generate_synthetic_rebar_grid()
    png_bytes = _encode_to_png_bytes(img)

    # Negative nominal spacing
    resp1 = client.post(
        "/api/v1/measure",
        files={"image": ("mat.png", png_bytes, "image/png")},
        data={"nominal_spacing_mm": "-150.0", "tolerance_mm": "15.0", "calibration_marker_mm": "50.0"},
    )
    assert resp1.status_code == 422

    # Negative tolerance
    resp2 = client.post(
        "/api/v1/measure",
        files={"image": ("mat.png", png_bytes, "image/png")},
        data={"nominal_spacing_mm": "150.0", "tolerance_mm": "-5.0", "calibration_marker_mm": "50.0"},
    )
    assert resp2.status_code == 422

    # Zero marker dimension
    resp3 = client.post(
        "/api/v1/measure",
        files={"image": ("mat.png", png_bytes, "image/png")},
        data={"nominal_spacing_mm": "150.0", "tolerance_mm": "15.0", "calibration_marker_mm": "0.0"},
    )
    assert resp3.status_code == 422


def test_api_measure_empty_file():
    """Verify empty file upload returns HTTP 400."""
    response = client.post(
        "/api/v1/measure",
        files={"image": ("empty.png", b"", "image/png")},
        data={"nominal_spacing_mm": "150.0", "tolerance_mm": "15.0", "calibration_marker_mm": "50.0"},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_api_get_inspection_by_id():
    """Verify cached inspection JSON retrieval and 404 for missing IDs."""
    # 404 for non-existent ID
    resp_missing = client.get("/api/v1/inspections/non-existent-id-999")
    assert resp_missing.status_code == 404

    # Perform a measure first
    img, _ = generate_synthetic_rebar_grid()
    resp_measure = client.post(
        "/api/v1/measure",
        files={"image": ("mat.png", _encode_to_png_bytes(img), "image/png")},
        data={"nominal_spacing_mm": "150.0", "tolerance_mm": "15.0", "calibration_marker_mm": "50.0"},
    )
    insp_id = resp_measure.json()["inspection_id"]

    # Retrieve by ID
    resp_get = client.get(f"/api/v1/inspections/{insp_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["inspection_id"] == insp_id
