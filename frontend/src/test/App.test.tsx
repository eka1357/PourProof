import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { App } from '../App';
import * as client from '../api/client';
import { InspectionResponse, HealthResponse } from '../types/api';

describe('App Inspection Workspace Integration Flow', () => {
  const mockHealth: HealthResponse = {
    status: 'ok',
    service: 'pourproof-api',
    opencv_version: '5.0.0.93',
  };

  const mockInspectionResult: InspectionResponse = {
    schema_version: '1.0',
    inspection_id: 'insp-e2e-1234',
    trace_id: 'trace-session-e2e',
    status: 'measured',
    calibration: {
      valid: true,
      method: 'aruco_marker',
      scale_mm_per_pixel: 0.852,
      pixels_per_mm: 1.174,
      marker_id: 0,
      marker_corners: [[100, 100], [200, 100], [200, 200], [100, 200]],
      warnings: [],
    },
    measurements: [
      {
        measurement_id: 'gap_001',
        direction: 'horizontal_spacing',
        spacing_mm: 199.1,
        nominal_spacing_mm: 200.0,
        deviation_mm: -0.9,
        tolerance_mm: 15.0,
        in_tolerance: true,
        measurement_quality: 'high',
        evidence_region: null,
      },
      {
        measurement_id: 'gap_002',
        direction: 'horizontal_spacing',
        spacing_mm: 202.4,
        nominal_spacing_mm: 200.0,
        deviation_mm: 2.4,
        tolerance_mm: 15.0,
        in_tolerance: true,
        measurement_quality: 'high',
        evidence_region: null,
      },
    ],
    quality_gate: {
      accepted: true,
      reason_codes: ['QUALITY_GATE_PASSED'],
      metrics: {
        blur_variance: 520.4,
        mean_brightness: 135.2,
        contrast_std: 48.6,
        image_width: 1024,
        image_height: 768,
      },
    },
    next_action: {
      action: 'DONE',
      reason_code: 'IN_TOLERANCE_VERIFIED',
    },
    summary: {
      measured_count: 2,
      in_tolerance_count: 2,
      out_of_tolerance_count: 0,
      mean_spacing_mm: 200.75,
      max_deviation_mm: 2.4,
    },
    trace: [
      {
        step_index: 1,
        tool: 'verify_opencv5_runtime',
        inputs_summary: {},
        output_status: 'ok',
        reason_code: null,
        duration_ms: 1.2,
        details: null,
      },
      {
        step_index: 2,
        tool: 'assess_image_quality',
        inputs_summary: { min_blur: 80.0 },
        output_status: 'passed',
        reason_code: 'QUALITY_GATE_PASSED',
        duration_ms: 8.5,
        details: { blur: 520.4 },
      },
      {
        step_index: 3,
        tool: 'detect_and_calibrate_marker',
        inputs_summary: { marker_size_mm: 100 },
        output_status: 'success',
        reason_code: 'MARKER_CALIBRATED',
        duration_ms: 15.3,
        details: { marker_id: 0, px_per_mm: 1.174 },
      },
    ],
    annotated_image_url: '/api/v1/inspections/insp-e2e-1234/annotated-image',
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(client, 'fetchHealth').mockResolvedValue(mockHealth);
  });

  it('renders header, upload zone, parameters, and limitations notice', async () => {
    render(<App />);

    expect(screen.getByText('PourProof')).toBeInTheDocument();
    expect(screen.getByText(/Concrete Rebar Inspection Workspace/i)).toBeInTheDocument();
    expect(screen.getByText(/Rebar Grid Photograph/i)).toBeInTheDocument();
    expect(screen.getByText(/Inspection Parameters & Calibration/i)).toBeInTheDocument();
    expect(screen.getByText(/Structural Engineering Operational Limitations/i)).toBeInTheDocument();

    // Verify health check succeeds
    await waitFor(() => {
      expect(screen.getByText(/OpenCV 5.0.0.93/i)).toBeInTheDocument();
    });
  });

  it('completes entire inspection flow: file select -> submit -> display results -> reset', async () => {
    const submitSpy = vi.spyOn(client, 'submitInspection').mockResolvedValue(mockInspectionResult);

    render(<App />);

    // 1. Select an image
    const file = new File(['mock-img'], 'slab_photo.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByLabelText(/Upload rebar grid photograph/i);
    fireEvent.change(fileInput, { target: { files: [file] } });

    // File should be displayed
    expect(screen.getByText('slab_photo.jpg')).toBeInTheDocument();

    // 2. Click Analyze Grid
    const analyzeButton = screen.getByRole('button', { name: /Analyze Grid/i });
    expect(analyzeButton).not.toBeDisabled();
    fireEvent.click(analyzeButton);

    // 3. Verify submitInspection was called with exact parameters
    expect(submitSpy).toHaveBeenCalledWith({
      imageFile: file,
      nominalSpacingMm: 200,
      toleranceMm: 15,
      calibrationMarkerMm: 100,
      sessionId: undefined,
    });

    // 4. Results rendered
    await waitFor(() => {
      expect(screen.getByTestId('status-badge')).toHaveTextContent('Complete');
    });

    // Verify metrics overview rendered
    expect(screen.getByText('200.8')).toBeInTheDocument(); // Mean detected spacing (200.75 rounded)
    expect(screen.getByText('+2.4')).toBeInTheDocument(); // Max deviation
    expect(screen.getByText('2 / 2')).toBeInTheDocument(); // Tolerance conformance

    // Verify measurement table rendered
    expect(screen.getByText('gap_001')).toBeInTheDocument();
    expect(screen.getByText('199.1 mm')).toBeInTheDocument();
    expect(screen.getByText('gap_002')).toBeInTheDocument();
    expect(screen.getByText('202.4 mm')).toBeInTheDocument();

    // Verify visual evidence inspector rendered
    expect(screen.getByText(/Visual Evidence Inspector/i)).toBeInTheDocument();

    // Verify Agent Trace rendered
    expect(screen.getByText(/Agentic Computer Vision Execution Trace/i)).toBeInTheDocument();
    expect(screen.getByText('verify_opencv5_runtime')).toBeInTheDocument();
    expect(screen.getByText('assess_image_quality')).toBeInTheDocument();

    // 5. Test Reset action
    const newInspectionBtn = screen.getByRole('button', { name: /New Inspection/i });
    fireEvent.click(newInspectionBtn);

    // Results should clear
    expect(screen.queryByTestId('status-badge')).not.toBeInTheDocument();
    expect(screen.getByText(/Drop inspection image here/i)).toBeInTheDocument();
  });

  it('displays API error message gracefully when submission fails', async () => {
    vi.spyOn(client, 'submitInspection').mockRejectedValue(
      new Error('Connection refused: FastAPI backend is down')
    );

    render(<App />);

    const file = new File(['mock-img'], 'slab_photo.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByLabelText(/Upload rebar grid photograph/i);
    fireEvent.change(fileInput, { target: { files: [file] } });

    const analyzeButton = screen.getByRole('button', { name: /Analyze Grid/i });
    fireEvent.click(analyzeButton);

    await waitFor(() => {
      expect(screen.getByText(/Inspection Execution Error/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Connection refused: FastAPI backend is down/i)
      ).toBeInTheDocument();
    });
  });
});
