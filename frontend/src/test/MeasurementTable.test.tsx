import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MeasurementTable } from '../components/MeasurementTable';
import { SpacingMeasurementItem } from '../types/api';

describe('MeasurementTable', () => {
  it('renders empty state when measurements list is empty', () => {
    render(<MeasurementTable measurements={[]} />);
    expect(screen.getByText(/No Measurements Available/i)).toBeInTheDocument();
  });

  it('renders rebar measurements distinguishing detected from nominal spacing', () => {
    const measurements: SpacingMeasurementItem[] = [
      {
        measurement_id: 'gap_001',
        direction: 'horizontal_spacing',
        spacing_mm: 198.4,
        nominal_spacing_mm: 200.0,
        deviation_mm: -1.6,
        tolerance_mm: 15.0,
        in_tolerance: true,
        measurement_quality: 'high',
        evidence_region: null,
      },
      {
        measurement_id: 'gap_002',
        direction: 'horizontal_spacing',
        spacing_mm: 222.0,
        nominal_spacing_mm: 200.0,
        deviation_mm: 22.0,
        tolerance_mm: 15.0,
        in_tolerance: false,
        measurement_quality: 'acceptable',
        evidence_region: null,
      },
    ];

    render(<MeasurementTable measurements={measurements} />);

    // Check IDs
    expect(screen.getByText('gap_001')).toBeInTheDocument();
    expect(screen.getByText('gap_002')).toBeInTheDocument();

    // Check Detected Physical Spacings
    expect(screen.getByText('198.4 mm')).toBeInTheDocument();
    expect(screen.getByText('222.0 mm')).toBeInTheDocument();

    // Check Nominal Spacings
    const nominalElements = screen.getAllByText('200.0 mm');
    expect(nominalElements.length).toBe(2);

    // Check Deviations
    expect(screen.getByText('-1.6 mm')).toBeInTheDocument();
    expect(screen.getByText('+22.0 mm')).toBeInTheDocument();

    // Check Tolerance indicators
    expect(screen.getByText('In Tolerance')).toBeInTheDocument();
    expect(screen.getByText('Out of Tolerance')).toBeInTheDocument();
  });
});
