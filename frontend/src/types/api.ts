/**
 * TypeScript type definitions for PourProof frontend.
 * Strictly adheres to API_CONTRACT.md and src/pourproof/api/schemas.py.
 */

export interface HealthResponse {
  status: 'ok' | 'unhealthy' | string;
  service: string;
  opencv_version: string;
}

export interface CalibrationInfo {
  valid: boolean;
  method: string;
  scale_mm_per_pixel: number | null;
  pixels_per_mm: number | null;
  marker_id: number | null;
  marker_corners: number[][] | null;
  warnings: string[];
}

export interface SpacingMeasurementItem {
  measurement_id: string;
  direction: 'horizontal_spacing' | 'vertical_spacing' | string;
  spacing_mm: number | null;
  nominal_spacing_mm: number | null;
  deviation_mm: number | null;
  tolerance_mm: number | null;
  in_tolerance: boolean;
  measurement_quality: 'high' | 'acceptable' | 'uncertain' | string;
  evidence_region: Record<string, unknown> | null;
}

export interface QualityGateMetrics {
  blur_variance?: number;
  mean_brightness?: number;
  contrast_std?: number;
  image_width?: number;
  image_height?: number;
  [key: string]: unknown;
}

export interface QualityGateInfo {
  accepted: boolean;
  reason_codes: string[];
  metrics: QualityGateMetrics | null;
}

export type NextActionType =
  | 'REPROCESS_CROP'
  | 'REQUEST_RECAPTURE'
  | 'REVIEW_MEASUREMENT'
  | 'HUMAN_REVIEW'
  | 'DONE';

export interface NextActionInfo {
  action: NextActionType;
  reason_code: string | null;
}

export interface TraceStep {
  step_index: number;
  tool: string;
  inputs_summary: Record<string, unknown>;
  output_status: string;
  reason_code: string | null;
  duration_ms: number;
  details: Record<string, unknown> | null;
}

export interface InspectionSummary {
  measured_count?: number;
  in_tolerance_count?: number;
  out_of_tolerance_count?: number;
  mean_spacing_mm?: number;
  max_deviation_mm?: number;
  overall_status?: string;
  [key: string]: unknown;
}

export type InspectionStatus =
  | 'measured'
  | 'needs_recapture'
  | 'needs_review'
  | 'rejected_input'
  | 'processing_error';

export interface InspectionResponse {
  schema_version: string;
  inspection_id: string;
  trace_id: string;
  status: InspectionStatus;
  calibration: CalibrationInfo;
  measurements: SpacingMeasurementItem[];
  quality_gate: QualityGateInfo;
  next_action: NextActionInfo;
  summary: InspectionSummary | null;
  trace: TraceStep[];
  annotated_image_url: string | null;
}

export interface ApiErrorDetail {
  error_code?: string;
  message?: string;
  detail?: string | Array<{ msg: string; loc: string[] }>;
}

export interface InspectionFormValues {
  imageFile: File;
  nominalSpacingMm: number;
  toleranceMm: number;
  calibrationMarkerMm: number;
  sessionId?: string;
}
