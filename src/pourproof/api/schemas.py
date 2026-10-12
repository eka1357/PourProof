"""Pydantic schemas for PourProof FastAPI backend conforming to API_CONTRACT.md."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Health endpoint response model."""
    status: str
    service: str = "pourproof-api"
    opencv_version: str


class CalibrationInfo(BaseModel):
    """Fiducial marker calibration metadata."""
    model_config = ConfigDict(extra="allow")

    valid: bool
    method: str = "aruco_marker"
    scale_mm_per_pixel: Optional[float] = None
    pixels_per_mm: Optional[float] = None
    marker_id: Optional[int] = None
    marker_corners: Optional[List[List[float]]] = None
    warnings: List[str] = Field(default_factory=list)


class SpacingMeasurementItem(BaseModel):
    """Individual rebar spacing measurement and deviation metadata."""
    model_config = ConfigDict(extra="allow")

    measurement_id: str
    direction: str  # "horizontal_spacing" or "vertical_spacing"
    spacing_mm: Optional[float] = None
    nominal_spacing_mm: Optional[float] = None
    deviation_mm: Optional[float] = None
    tolerance_mm: Optional[float] = None
    in_tolerance: bool
    measurement_quality: str  # "high", "acceptable", "uncertain"
    evidence_region: Optional[Dict[str, Any]] = None


class QualityGateInfo(BaseModel):
    """Image quality evaluation gate results."""
    model_config = ConfigDict(extra="allow")

    accepted: bool
    reason_codes: List[str] = Field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None


class NextActionInfo(BaseModel):
    """Controller decision for subsequent action."""
    action: str  # "REPROCESS_CROP", "REQUEST_RECAPTURE", "REVIEW_MEASUREMENT", "HUMAN_REVIEW", "DONE"
    reason_code: Optional[str] = None


class TraceStep(BaseModel):
    """Single inspectable agent trace event."""
    model_config = ConfigDict(extra="allow")

    step_index: int
    tool: str
    inputs_summary: Dict[str, Any]
    output_status: str
    reason_code: Optional[str] = None
    duration_ms: float
    details: Optional[Dict[str, Any]] = None


class InspectionResponse(BaseModel):
    """Full calibrated inspection response model matching API_CONTRACT.md."""
    model_config = ConfigDict(extra="allow")

    schema_version: str = "1.0"
    inspection_id: str
    trace_id: str
    status: str  # "measured", "needs_recapture", "needs_review", "rejected_input", "processing_error"
    calibration: CalibrationInfo
    measurements: List[SpacingMeasurementItem] = Field(default_factory=list)
    quality_gate: QualityGateInfo
    next_action: NextActionInfo
    summary: Optional[Dict[str, Any]] = None
    trace: List[TraceStep] = Field(default_factory=list)
    annotated_image_url: Optional[str] = None


class ErrorResponse(BaseModel):
    """Structured machine-readable API error."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
