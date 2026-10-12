"""Deterministic controller and inspection pipeline for PourProof.

Coordinates OpenCV 5 tools, logs every step into an inspectable agent trace,
and enforces explicit abstention and human-review gates.
"""

from dataclasses import asdict
import time
import uuid
from typing import Dict, Any, Optional, List, Union
import cv2
import numpy as np

from pourproof.vision.runtime import verify_opencv5_runtime, get_opencv_runtime_info
from pourproof.vision.quality import evaluate_image_quality
from pourproof.vision.calibration import detect_calibration_marker
from pourproof.vision.rectification import rectify_planar_view
from pourproof.vision.detection import detect_rebar_grid
from pourproof.vision.measurement import compute_rebar_spacings
from pourproof.vision.annotator import draw_inspection_annotations


def run_inspection_pipeline(
    image_input: Union[bytes, np.ndarray],
    nominal_spacing_mm: float,
    tolerance_mm: float,
    calibration_marker_mm: float,
    session_id: Optional[str] = None,
    allow_rectification: bool = True,
) -> Dict[str, Any]:
    """Execute the multi-stage calibrated inspection pipeline.
    
    Args:
        image_input: Raw image bytes or decoded NumPy array (BGR).
        nominal_spacing_mm: User-entered nominal center-to-center spacing.
        tolerance_mm: User-entered permissible tolerance (+/- mm).
        calibration_marker_mm: Physical dimension of coplanar marker in mm.
        session_id: Optional caller-supplied identifier.
        allow_rectification: Whether to apply perspective rectification when needed.
        
    Returns:
        Structured inspection response conforming to API_CONTRACT.md.
    """
    inspection_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    trace: List[Dict[str, Any]] = []

    def _record_trace_step(
        tool: str,
        inputs_summary: Dict[str, Any],
        output_status: str,
        reason_code: Optional[str],
        duration_ms: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        trace.append({
            "step_index": len(trace) + 1,
            "tool": tool,
            "inputs_summary": inputs_summary,
            "output_status": output_status,
            "reason_code": reason_code,
            "duration_ms": round(duration_ms, 2),
            "details": details or {},
        })

    # Pre-step: Validate OpenCV 5 runtime
    t0 = time.perf_counter()
    runtime_info = get_opencv_runtime_info()
    _record_trace_step(
        tool="OpenCVRuntimeVerification",
        inputs_summary={},
        output_status="OK" if runtime_info["is_opencv5"] else "FAILED",
        reason_code=None if runtime_info["is_opencv5"] else "OPENCV5_NOT_ACTIVE",
        duration_ms=(time.perf_counter() - t0) * 1000,
        details={"version": runtime_info["version"], "path": runtime_info["module_path"]},
    )
    if not runtime_info["is_opencv5"]:
        return {
            "schema_version": "1.0",
            "inspection_id": inspection_id,
            "trace_id": trace_id,
            "status": "processing_error",
            "quality_gate": {"accepted": False, "reason_codes": ["OPENCV5_NOT_ACTIVE"]},
            "calibration": {"valid": False, "method": "none", "scale_mm_per_pixel": None, "warnings": []},
            "measurements": [],
            "next_action": {"action": "HUMAN_REVIEW", "reason_code": "OPENCV5_NOT_ACTIVE"},
            "trace": trace,
        }

    # Input validation: Numeric parameters
    if nominal_spacing_mm <= 0 or tolerance_mm < 0 or calibration_marker_mm <= 0:
        return {
            "schema_version": "1.0",
            "inspection_id": inspection_id,
            "trace_id": trace_id,
            "status": "rejected_input",
            "quality_gate": {"accepted": False, "reason_codes": ["INVALID_INPUT_PARAMETERS"]},
            "calibration": {"valid": False, "method": "none", "scale_mm_per_pixel": None, "warnings": []},
            "measurements": [],
            "next_action": {"action": "REQUEST_RECAPTURE", "reason_code": "INVALID_INPUT_PARAMETERS"},
            "trace": trace,
        }

    # Image decoding
    t0 = time.perf_counter()
    if isinstance(image_input, bytes):
        nparr = np.frombuffer(image_input, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif isinstance(image_input, np.ndarray):
        image = image_input.copy()
    else:
        image = None

    if image is None or image.size == 0:
        _record_trace_step(
            tool="ImageDecoder",
            inputs_summary={"input_type": str(type(image_input))},
            output_status="FAILED",
            reason_code="IMAGE_DECODE_FAILED",
            duration_ms=(time.perf_counter() - t0) * 1000,
        )
        return {
            "schema_version": "1.0",
            "inspection_id": inspection_id,
            "trace_id": trace_id,
            "status": "rejected_input",
            "quality_gate": {"accepted": False, "reason_codes": ["IMAGE_DECODE_FAILED"]},
            "calibration": {"valid": False, "method": "none", "scale_mm_per_pixel": None, "warnings": []},
            "measurements": [],
            "next_action": {"action": "REQUEST_RECAPTURE", "reason_code": "IMAGE_DECODE_FAILED"},
            "trace": trace,
        }

    _record_trace_step(
        tool="ImageDecoder",
        inputs_summary={"width": image.shape[1], "height": image.shape[0]},
        output_status="SUCCESS",
        reason_code=None,
        duration_ms=(time.perf_counter() - t0) * 1000,
    )

    # Stage 1: Quality Gate
    t0 = time.perf_counter()
    quality = evaluate_image_quality(image)
    _record_trace_step(
        tool="ImageQualityGate",
        inputs_summary={"width": image.shape[1], "height": image.shape[0]},
        output_status="ACCEPTED" if quality.accepted else "REJECTED",
        reason_code=quality.reason_codes[0] if quality.reason_codes else None,
        duration_ms=(time.perf_counter() - t0) * 1000,
        details=quality.metrics,
    )

    if not quality.accepted:
        primary_reason = quality.reason_codes[0]
        return {
            "schema_version": "1.0",
            "inspection_id": inspection_id,
            "trace_id": trace_id,
            "status": "needs_recapture",
            "quality_gate": {
                "accepted": False,
                "reason_codes": quality.reason_codes,
                "metrics": quality.metrics,
            },
            "calibration": {"valid": False, "method": "none", "scale_mm_per_pixel": None, "warnings": []},
            "measurements": [],
            "next_action": {"action": "REQUEST_RECAPTURE", "reason_code": primary_reason},
            "trace": trace,
        }

    # Stage 2: Calibration
    t0 = time.perf_counter()
    calib = detect_calibration_marker(image, marker_dimension_mm=calibration_marker_mm)
    _record_trace_step(
        tool="MarkerCalibration",
        inputs_summary={"marker_dimension_mm": calibration_marker_mm},
        output_status="VALID" if calib.valid else "FAILED",
        reason_code=calib.reason_codes[0] if calib.reason_codes else None,
        duration_ms=(time.perf_counter() - t0) * 1000,
        details={
            "scale_mm_per_pixel": calib.scale_mm_per_pixel,
            "marker_id": calib.marker_id,
            "aspect_ratio_divergence": calib.aspect_ratio_divergence,
        },
    )

    if not calib.valid:
        primary_reason = calib.reason_codes[0] if calib.reason_codes else "CALIBRATION_FAILED"
        return {
            "schema_version": "1.0",
            "inspection_id": inspection_id,
            "trace_id": trace_id,
            "status": "needs_recapture",
            "quality_gate": {
                "accepted": True,
                "reason_codes": [],
                "metrics": quality.metrics,
            },
            "calibration": {
                "valid": False,
                "method": calib.method,
                "scale_mm_per_pixel": None,
                "warnings": calib.warnings,
            },
            "measurements": [],
            "next_action": {"action": "REQUEST_RECAPTURE", "reason_code": primary_reason},
            "trace": trace,
        }

    # Stage 3: Perspective Rectification
    analysis_image = image
    active_scale = calib.scale_mm_per_pixel
    rectification_applied = False
    
    # Apply rectification if perspective foreshortening detected or requested
    if allow_rectification and calib.marker_corners:
        t0 = time.perf_counter()
        rect_result = rectify_planar_view(
            image=image,
            marker_corners=calib.marker_corners,
            marker_dimension_mm=calibration_marker_mm,
        )
        if rect_result.success and rect_result.rectified_image is not None:
            analysis_image = rect_result.rectified_image
            active_scale = rect_result.rectified_scale_mm_per_pixel
            rectification_applied = True
            _record_trace_step(
                tool="PlanarRectification",
                inputs_summary={"aspect_ratio_divergence": calib.aspect_ratio_divergence},
                output_status="SUCCESS",
                reason_code=None,
                duration_ms=(time.perf_counter() - t0) * 1000,
                details={"rectified_scale_mm_per_pixel": active_scale},
            )
        elif "PERSPECTIVE_DISTORTION_TOO_HIGH" in rect_result.reason_codes:
            _record_trace_step(
                tool="PlanarRectification",
                inputs_summary={"aspect_ratio_divergence": calib.aspect_ratio_divergence},
                output_status="FAILED",
                reason_code="PERSPECTIVE_DISTORTION_TOO_HIGH",
                duration_ms=(time.perf_counter() - t0) * 1000,
                details={"warnings": rect_result.warnings},
            )
            return {
                "schema_version": "1.0",
                "inspection_id": inspection_id,
                "trace_id": trace_id,
                "status": "needs_recapture",
                "quality_gate": {"accepted": True, "reason_codes": [], "metrics": quality.metrics},
                "calibration": asdict(calib),
                "measurements": [],
                "next_action": {
                    "action": "REQUEST_RECAPTURE",
                    "reason_code": "PERSPECTIVE_DISTORTION_TOO_HIGH",
                },
                "trace": trace,
            }

    # Stage 4: Rebar Grid Detection
    t0 = time.perf_counter()
    grid = detect_rebar_grid(analysis_image)
    _record_trace_step(
        tool="GridDetection",
        inputs_summary={"rectification_applied": rectification_applied},
        output_status="SUCCESS" if grid.success else "INSUFFICIENT",
        reason_code=grid.reason_codes[0] if grid.reason_codes else None,
        duration_ms=(time.perf_counter() - t0) * 1000,
        details={
            "vertical_bar_count": len(grid.vertical_bars),
            "horizontal_bar_count": len(grid.horizontal_bars),
        },
    )

    if not grid.success:
        primary_reason = grid.reason_codes[0] if grid.reason_codes else "INSUFFICIENT_GRID_BARS_DETECTED"
        return {
            "schema_version": "1.0",
            "inspection_id": inspection_id,
            "trace_id": trace_id,
            "status": "needs_review",
            "quality_gate": {"accepted": True, "reason_codes": [], "metrics": quality.metrics},
            "calibration": asdict(calib),
            "measurements": [],
            "next_action": {"action": "HUMAN_REVIEW", "reason_code": primary_reason},
            "trace": trace,
        }

    # Stage 5: Spacing Measurements
    t0 = time.perf_counter()
    measurement_result = compute_rebar_spacings(
        vertical_bar_positions=grid.vertical_positions,
        horizontal_bar_positions=grid.horizontal_positions,
        scale_mm_per_pixel=active_scale,
        nominal_spacing_mm=nominal_spacing_mm,
        tolerance_mm=tolerance_mm,
    )
    _record_trace_step(
        tool="SpacingMeasurement",
        inputs_summary={
            "nominal_spacing_mm": nominal_spacing_mm,
            "tolerance_mm": tolerance_mm,
            "scale_mm_per_pixel": active_scale,
        },
        output_status="SUCCESS" if measurement_result.success else "FAILED",
        reason_code=measurement_result.reason_codes[0] if measurement_result.reason_codes else None,
        duration_ms=(time.perf_counter() - t0) * 1000,
        details={
            "gaps_measured": len(measurement_result.measurements),
            "all_in_tolerance": measurement_result.summary.all_in_tolerance if measurement_result.summary else False,
        },
    )

    if not measurement_result.success:
        primary_reason = measurement_result.reason_codes[0] if measurement_result.reason_codes else "MEASUREMENT_FAILED"
        return {
            "schema_version": "1.0",
            "inspection_id": inspection_id,
            "trace_id": trace_id,
            "status": "needs_review",
            "quality_gate": {"accepted": True, "reason_codes": [], "metrics": quality.metrics},
            "calibration": asdict(calib),
            "measurements": [],
            "next_action": {"action": "HUMAN_REVIEW", "reason_code": primary_reason},
            "trace": trace,
        }

    # Determine final disposition and next action
    measurements_serialized = [asdict(m) for m in measurement_result.measurements]
    has_uncertain = any(m.measurement_quality == "uncertain" for m in measurement_result.measurements)
    all_in_tol = measurement_result.summary.all_in_tolerance if measurement_result.summary else False

    if has_uncertain:
        final_status = "needs_review"
        next_action = {"action": "REVIEW_MEASUREMENT", "reason_code": "MEASUREMENT_UNCERTAIN"}
    elif not all_in_tol:
        final_status = "needs_review"
        next_action = {"action": "REVIEW_MEASUREMENT", "reason_code": "SPACING_OUT_OF_TOLERANCE"}
    else:
        final_status = "measured"
        next_action = {"action": "DONE", "reason_code": "ALL_SPACINGS_IN_TOLERANCE"}

    # Stage 6: Annotation Overlay
    t0 = time.perf_counter()
    annotated_img = draw_inspection_annotations(
        image=analysis_image,
        measurements=measurement_result.measurements,
        vertical_positions=grid.vertical_positions,
        horizontal_positions=grid.horizontal_positions,
        marker_corners=calib.marker_corners if not rectification_applied else None,
        marker_id=calib.marker_id,
        inspection_status=final_status,
    )
    _record_trace_step(
        tool="AnnotationRendering",
        inputs_summary={"measurements_count": len(measurements_serialized)},
        output_status="SUCCESS",
        reason_code=None,
        duration_ms=(time.perf_counter() - t0) * 1000,
    )

    # Encode annotated image as PNG bytes
    success, encoded_buf = cv2.imencode(".png", annotated_img)
    annotated_bytes = encoded_buf.tobytes() if success else None

    return {
        "schema_version": "1.0",
        "inspection_id": inspection_id,
        "trace_id": trace_id,
        "status": final_status,
        "quality_gate": {
            "accepted": True,
            "reason_codes": [],
            "metrics": quality.metrics,
        },
        "calibration": asdict(calib),
        "rectification_applied": rectification_applied,
        "measurements": measurements_serialized,
        "summary": asdict(measurement_result.summary) if measurement_result.summary else None,
        "next_action": next_action,
        "trace": trace,
        "annotated_image_bytes": annotated_bytes,
    }
