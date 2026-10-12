"""FastAPI route handlers for PourProof endpoints."""

import math
from typing import Optional
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status
from fastapi.responses import Response, JSONResponse

from pourproof.vision.runtime import get_opencv_runtime_info
from pourproof.vision.pipeline import run_inspection_pipeline
from pourproof.api.schemas import (
    HealthResponse,
    InspectionResponse,
    ErrorResponse,
)
from pourproof.api.storage import inspection_store

router = APIRouter()

MAX_IMAGE_BYTES = 25 * 1024 * 1024  # 25 MB safety limit


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Reports service status and verified runtime OpenCV version.",
)
async def get_health() -> JSONResponse:
    """Check API readiness and verified OpenCV 5 runtime status."""
    runtime = get_opencv_runtime_info()
    if runtime["is_opencv5"]:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "service": "pourproof-api",
                "opencv_version": runtime["version"],
            },
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "unhealthy",
            "service": "pourproof-api",
            "opencv_version": runtime["version"],
        },
    )


@router.post(
    "/api/v1/measure",
    response_model=InspectionResponse,
    summary="Run calibrated rebar measurement",
    description="Processes uploaded image and validates rebar spacing using OpenCV 5 pipeline.",
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
)
async def measure_rebar(
    image: UploadFile = File(..., description="Uploaded JPEG, PNG, or WebP image"),
    nominal_spacing_mm: float = Form(..., description="User-entered design center-to-center spacing in mm"),
    tolerance_mm: float = Form(..., description="User-entered allowable tolerance (+/- mm)"),
    calibration_marker_mm: float = Form(..., description="Known physical dimension of coplanar marker in mm"),
    session_id: Optional[str] = Form(None, description="Optional session or retry grouping ID"),
) -> InspectionResponse:
    """Execute the multi-stage vision inspection pipeline on an uploaded mat photograph."""
    # 1. Parameter Validation
    if math.isnan(nominal_spacing_mm) or math.isinf(nominal_spacing_mm) or nominal_spacing_mm <= 0:
        raise HTTPException(
            status_code=422,
            detail="nominal_spacing_mm must be a positive finite number.",
        )
    if math.isnan(tolerance_mm) or math.isinf(tolerance_mm) or tolerance_mm < 0:
        raise HTTPException(
            status_code=422,
            detail="tolerance_mm must be a non-negative finite number.",
        )
    if math.isnan(calibration_marker_mm) or math.isinf(calibration_marker_mm) or calibration_marker_mm <= 0:
        raise HTTPException(
            status_code=422,
            detail="calibration_marker_mm must be a positive finite number.",
        )

    # 2. File Read & Byte Size Validation
    try:
        contents = await image.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded image: {str(e)}",
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowable size of {MAX_IMAGE_BYTES // (1024 * 1024)} MB.",
        )

    # 3. Invoke Vision Pipeline
    pipeline_result = run_inspection_pipeline(
        image_input=contents,
        nominal_spacing_mm=nominal_spacing_mm,
        tolerance_mm=tolerance_mm,
        calibration_marker_mm=calibration_marker_mm,
        session_id=session_id,
    )

    inspection_id = pipeline_result["inspection_id"]
    annotated_bytes = pipeline_result.pop("annotated_image_bytes", None)

    # 4. Ephemeral Storage & Annotated URL Generation
    annotated_url = None
    if annotated_bytes:
        inspection_store.store(
            inspection_id=inspection_id,
            result=pipeline_result,
            image_bytes=annotated_bytes,
        )
        annotated_url = f"/api/v1/inspections/{inspection_id}/annotated-image"
    else:
        inspection_store.store(
            inspection_id=inspection_id,
            result=pipeline_result,
        )

    pipeline_result["annotated_image_url"] = annotated_url

    return InspectionResponse(**pipeline_result)


@router.get(
    "/api/v1/inspections/{inspection_id}/annotated-image",
    summary="Get annotated inspection evidence image",
    description="Returns the rendered PNG overlay for a completed inspection.",
    responses={
        200: {"content": {"image/png": {}}},
        404: {"model": ErrorResponse},
    },
)
async def get_annotated_image(inspection_id: str) -> Response:
    """Stream the generated annotated inspection image as PNG."""
    image_bytes = inspection_store.get_image(inspection_id)
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No annotated image found for inspection ID '{inspection_id}'.",
        )
    return Response(content=image_bytes, media_type="image/png")


@router.get(
    "/api/v1/inspections/{inspection_id}",
    response_model=InspectionResponse,
    summary="Get inspection result by ID",
    description="Retrieves a cached inspection result by ID.",
)
async def get_inspection(inspection_id: str) -> InspectionResponse:
    """Retrieve the cached inspection result JSON."""
    result = inspection_store.get_result(inspection_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection ID '{inspection_id}' not found.",
        )
    return InspectionResponse(**result)
