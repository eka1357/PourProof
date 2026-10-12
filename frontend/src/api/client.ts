/**
 * API client communicating with FastAPI backend.
 * Provides typed methods for /api/health and /api/v1/measure.
 */

import { HealthResponse, InspectionResponse, InspectionFormValues } from '../types/api';

const API_BASE = '';

/**
 * Fetch backend liveness and verified OpenCV 5 runtime info.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/health`, {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const json = await response.json();
      if (json.detail) errorDetail = typeof json.detail === 'string' ? json.detail : JSON.stringify(json.detail);
      else if (json.message) errorDetail = json.message;
    } catch {
      // Use fallback errorDetail
    }
    throw new Error(`API health check failed: ${errorDetail}`);
  }

  return response.json();
}

/**
 * Submit an inspection image and calibration parameters to POST /api/v1/measure.
 */
export async function submitInspection(values: InspectionFormValues): Promise<InspectionResponse> {
  const formData = new FormData();
  formData.append('image', values.imageFile);
  formData.append('nominal_spacing_mm', values.nominalSpacingMm.toString());
  formData.append('tolerance_mm', values.toleranceMm.toString());
  formData.append('calibration_marker_mm', values.calibrationMarkerMm.toString());

  if (values.sessionId && values.sessionId.trim().length > 0) {
    formData.append('session_id', values.sessionId.trim());
  }

  const response = await fetch(`${API_BASE}/api/v1/measure`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = `Inspection request failed with HTTP ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        if (typeof errJson.detail === 'string') {
          errorDetail = errJson.detail;
        } else if (Array.isArray(errJson.detail)) {
          errorDetail = errJson.detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join('; ');
        } else {
          errorDetail = JSON.stringify(errJson.detail);
        }
      } else if (errJson.message) {
        errorDetail = errJson.message;
      }
    } catch {
      // response might be non-JSON
    }
    throw new Error(errorDetail);
  }

  const result: InspectionResponse = await response.json();
  return result;
}

/**
 * Construct URL for the annotated inspection image.
 */
export function getAnnotatedImageUrl(pathOrId: string): string {
  if (pathOrId.startsWith('/api')) {
    return pathOrId;
  }
  return `/api/v1/inspections/${pathOrId}/annotated-image`;
}
