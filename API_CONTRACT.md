# PourProof API Contract (Initial Draft)

This is an implementation contract, not a claim that these endpoints already exist. Build them only after the first vision spike passes. Keep the vision code independent from FastAPI route functions.

## Initial endpoints

### `GET /api/health`

Purpose: liveness/readiness for local development and deployment checks.

Example response:

```json
{
  "status": "ok",
  "service": "pourproof-api",
  "opencv_version": "verified-runtime-version"
}
```

`opencv_version` must be read from the runtime, not hardcoded. If the required OpenCV 5 runtime cannot be verified, report an unhealthy/degraded status instead of claiming success.

### `POST /api/v1/measure`

Purpose: run one calibrated image measurement using the OpenCV pipeline.

Request: `multipart/form-data`

- `image`: uploaded image file.
- `nominal_spacing_mm`: positive finite user-entered design spacing.
- `tolerance_mm`: non-negative finite user-entered tolerance.
- `calibration_marker_mm`: positive finite known marker dimension visible on the same plane.
- `session_id`: optional opaque ID for grouping retries in the demo.

Validate decoded file format, byte size, pixel dimensions, numeric fields and calibration-marker visibility. Do not trust file extension or browser-supplied MIME type alone. Reject unsupported inputs with safe error messages.

Success response should be typed and versioned. Example shape only:

```json
{
  "schema_version": "1.0",
  "inspection_id": "server-generated-id",
  "status": "needs_review",
  "calibration": {
    "valid": true,
    "method": "marker_plane",
    "scale_mm_per_pixel": null,
    "warnings": []
  },
  "measurements": [
    {
      "measurement_id": "m1",
      "spacing_mm": null,
      "nominal_spacing_mm": null,
      "deviation_mm": null,
      "measurement_quality": "not_yet_available",
      "evidence_region": null
    }
  ],
  "quality_gate": {
    "accepted": false,
    "reason_codes": ["REPLACE_WITH_ACTUAL_REASON_CODE"]
  },
  "next_action": {
    "action": "HUMAN_REVIEW",
    "reason_code": "REPLACE_WITH_ACTUAL_REASON_CODE"
  },
  "trace_id": "server-generated-id"
}
```

The values above are placeholders to illustrate the schema; actual responses must contain measured values or explicit nulls. Never use placeholder values in the UI as if they were results. Choose final field names/types during implementation and keep frontend/backend schemas in sync.

Potential `status` values: `measured`, `needs_recapture`, `needs_review`, `rejected_input`, `processing_error`.

Allowed `next_action` values: `REPROCESS_CROP`, `REQUEST_RECAPTURE`, `REVIEW_MEASUREMENT`, `HUMAN_REVIEW`, `DONE`.

## Agent trace

Record for each step:

- input image digest or non-sensitive fixture ID (avoid logging image bytes or private paths),
- OpenCV tool and version,
- relevant thresholds/configuration,
- structured tool result and reason codes,
- controller-selected next action,
- whether the action succeeded, retry count and terminal disposition.

The controller, not an LLM, must enforce the allowed actions and stop conditions.

## Error behavior

Use appropriate HTTP status codes and stable machine-readable error codes. Do not return Python tracebacks, AWS details, secrets, local paths or model-provider responses directly to the browser. Add timeouts and upload limits. Avoid persisting uploads by default.

## Not in the first API version

No login system, SQL database, queue, public upload URL, S3 persistence, payment mechanism or external LLM call is needed for the first local measurement prototype.
