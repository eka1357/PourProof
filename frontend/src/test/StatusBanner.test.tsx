import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBanner, deriveDisplayStatus } from '../components/StatusBanner';
import { InspectionResponse } from '../types/api';

describe('StatusBanner and deriveDisplayStatus', () => {
  const baseInspection: InspectionResponse = {
    schema_version: '1.0',
    inspection_id: 'insp-12345678',
    trace_id: 'trace-12345678',
    status: 'measured',
    calibration: {
      valid: true,
      method: 'aruco_marker',
      scale_mm_per_pixel: 0.85,
      pixels_per_mm: 1.18,
      marker_id: 0,
      marker_corners: [[0, 0], [10, 0], [10, 10], [0, 10]],
      warnings: [],
    },
    measurements: [
      {
        measurement_id: 'gap_001',
        direction: 'horizontal_spacing',
        spacing_mm: 201.2,
        nominal_spacing_mm: 200.0,
        deviation_mm: 1.2,
        tolerance_mm: 15.0,
        in_tolerance: true,
        measurement_quality: 'high',
        evidence_region: null,
      },
    ],
    quality_gate: {
      accepted: true,
      reason_codes: ['QUALITY_GATE_PASSED'],
      metrics: { blur_variance: 450.0 },
    },
    next_action: {
      action: 'DONE',
      reason_code: 'IN_TOLERANCE_VERIFIED',
    },
    summary: {
      measured_count: 1,
      in_tolerance_count: 1,
      out_of_tolerance_count: 0,
      mean_spacing_mm: 201.2,
      max_deviation_mm: 1.2,
    },
    trace: [],
    annotated_image_url: '/api/v1/inspections/insp-12345678/annotated-image',
  };

  it('renders "Complete" when all measurements are in tolerance and calibration valid', () => {
    expect(deriveDisplayStatus(baseInspection)).toBe('Complete');

    render(<StatusBanner inspection={baseInspection} />);
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('Complete');
    // Ensure "PASS: SAFE" is NEVER rendered
    expect(screen.queryByText(/PASS: SAFE/i)).not.toBeInTheDocument();
  });

  it('renders "Complete with flags" when out-of-tolerance gaps exist', () => {
    const flaggedInspection: InspectionResponse = {
      ...baseInspection,
      next_action: {
        action: 'REVIEW_MEASUREMENT',
        reason_code: 'REBAR_OUT_OF_TOLERANCE',
      },
      summary: {
        ...baseInspection.summary,
        out_of_tolerance_count: 1,
      },
    };

    expect(deriveDisplayStatus(flaggedInspection)).toBe('Complete with flags');
    render(<StatusBanner inspection={flaggedInspection} />);
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Complete with flags');
  });

  it('renders "Retake image" when quality gate fails', () => {
    const lowQualityInspection: InspectionResponse = {
      ...baseInspection,
      status: 'needs_recapture',
      quality_gate: {
        accepted: false,
        reason_codes: ['BLUR_DETECTED'],
        metrics: { blur_variance: 45.0 },
      },
      next_action: {
        action: 'REQUEST_RECAPTURE',
        reason_code: 'BLUR_DETECTED',
      },
    };

    expect(deriveDisplayStatus(lowQualityInspection)).toBe('Retake image');
    render(<StatusBanner inspection={lowQualityInspection} />);
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Retake image');
  });

  it('renders "Retake image" when fiducial calibration is invalid', () => {
    const uncalibratedInspection: InspectionResponse = {
      ...baseInspection,
      status: 'needs_recapture',
      calibration: {
        ...baseInspection.calibration,
        valid: false,
        scale_mm_per_pixel: null,
      },
      next_action: {
        action: 'REQUEST_RECAPTURE',
        reason_code: 'ARUCO_NOT_DETECTED',
      },
    };

    expect(deriveDisplayStatus(uncalibratedInspection)).toBe('Retake image');
    render(<StatusBanner inspection={uncalibratedInspection} />);
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Retake image');
  });

  it('renders "Needs human review" when action is HUMAN_REVIEW', () => {
    const reviewInspection: InspectionResponse = {
      ...baseInspection,
      status: 'needs_review',
      next_action: {
        action: 'HUMAN_REVIEW',
        reason_code: 'UNCERTAIN_EDGE_MEASUREMENT',
      },
    };

    expect(deriveDisplayStatus(reviewInspection)).toBe('Needs human review');
    render(<StatusBanner inspection={reviewInspection} />);
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Needs human review');
  });

  it('renders "Failed" on processing_error or rejected_input', () => {
    const failedInspection: InspectionResponse = {
      ...baseInspection,
      status: 'processing_error',
      next_action: {
        action: 'HUMAN_REVIEW',
        reason_code: 'PIPELINE_ERROR',
      },
    };

    expect(deriveDisplayStatus(failedInspection)).toBe('Failed');
    render(<StatusBanner inspection={failedInspection} />);
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Failed');
  });
});
