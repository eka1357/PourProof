import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ParameterForm } from '../components/ParameterForm';

describe('ParameterForm', () => {
  it('renders input fields with initial values', () => {
    render(
      <ParameterForm
        nominalSpacing={200}
        tolerance={15}
        markerDimension={100}
        sessionId="TEST-GRID"
        onNominalSpacingChange={vi.fn()}
        onToleranceChange={vi.fn()}
        onMarkerDimensionChange={vi.fn()}
        onSessionIdChange={vi.fn()}
        onSubmit={vi.fn()}
        canSubmit={true}
        isSubmitting={false}
      />
    );

    const nominalInput = screen.getByLabelText(/Nominal Spacing/i) as HTMLInputElement;
    const toleranceInput = screen.getByLabelText(/Tolerance/i) as HTMLInputElement;
    const markerInput = screen.getByLabelText(/Marker Size/i) as HTMLInputElement;

    expect(nominalInput.value).toBe('200');
    expect(toleranceInput.value).toBe('15');
    expect(markerInput.value).toBe('100');
  });

  it('triggers change handlers when values are modified', () => {
    const handleNominal = vi.fn();
    const handleTolerance = vi.fn();

    render(
      <ParameterForm
        nominalSpacing={200}
        tolerance={15}
        markerDimension={100}
        sessionId=""
        onNominalSpacingChange={handleNominal}
        onToleranceChange={handleTolerance}
        onMarkerDimensionChange={vi.fn()}
        onSessionIdChange={vi.fn()}
        onSubmit={vi.fn()}
        canSubmit={true}
        isSubmitting={false}
      />
    );

    const nominalInput = screen.getByLabelText(/Nominal Spacing/i);
    fireEvent.change(nominalInput, { target: { value: '250' } });
    expect(handleNominal).toHaveBeenCalledWith(250);

    const toleranceInput = screen.getByLabelText(/Tolerance/i);
    fireEvent.change(toleranceInput, { target: { value: '20' } });
    expect(handleTolerance).toHaveBeenCalledWith(20);
  });

  it('applies preset specification values when preset button is clicked', () => {
    const handleNominal = vi.fn();
    const handleTolerance = vi.fn();
    const handleMarker = vi.fn();

    render(
      <ParameterForm
        nominalSpacing={200}
        tolerance={15}
        markerDimension={100}
        sessionId=""
        onNominalSpacingChange={handleNominal}
        onToleranceChange={handleTolerance}
        onMarkerDimensionChange={handleMarker}
        onSessionIdChange={vi.fn()}
        onSubmit={vi.fn()}
        canSubmit={true}
        isSubmitting={false}
      />
    );

    const shearWallPreset = screen.getByRole('button', { name: /High Shear Wall/i });
    fireEvent.click(shearWallPreset);

    expect(handleNominal).toHaveBeenCalledWith(150);
    expect(handleTolerance).toHaveBeenCalledWith(10);
    expect(handleMarker).toHaveBeenCalledWith(100);
  });

  it('disables submit button when canSubmit is false', () => {
    render(
      <ParameterForm
        nominalSpacing={0}
        tolerance={-5}
        markerDimension={100}
        sessionId=""
        onNominalSpacingChange={vi.fn()}
        onToleranceChange={vi.fn()}
        onMarkerDimensionChange={vi.fn()}
        onSessionIdChange={vi.fn()}
        onSubmit={vi.fn()}
        canSubmit={false}
        isSubmitting={false}
      />
    );

    const button = screen.getByRole('button', { name: /Analyze Grid/i });
    expect(button).toBeDisabled();
  });
});
