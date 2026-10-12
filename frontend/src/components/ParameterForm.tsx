import React from 'react';
import { Sliders, Crosshair, ArrowRight, Sparkles } from 'lucide-react';

interface ParameterFormProps {
  nominalSpacing: number;
  tolerance: number;
  markerDimension: number;
  sessionId: string;
  onNominalSpacingChange: (val: number) => void;
  onToleranceChange: (val: number) => void;
  onMarkerDimensionChange: (val: number) => void;
  onSessionIdChange: (val: string) => void;
  onSubmit: () => void;
  canSubmit: boolean;
  isSubmitting: boolean;
}

interface Preset {
  label: string;
  nominal: number;
  tolerance: number;
  marker: number;
  description: string;
}

const PRESETS: Preset[] = [
  {
    label: 'Standard Slab (200 ±15mm)',
    nominal: 200,
    tolerance: 15,
    marker: 100,
    description: 'Typical residential/commercial floor slab rebar mat',
  },
  {
    label: 'High Shear Wall (150 ±10mm)',
    nominal: 150,
    tolerance: 10,
    marker: 100,
    description: 'Dense structural shear wall reinforcement grid',
  },
  {
    label: 'Foundation Footing (300 ±25mm)',
    nominal: 300,
    tolerance: 25,
    marker: 100,
    description: 'Heavy foundation mat rebar spacing',
  },
];

export const ParameterForm: React.FC<ParameterFormProps> = ({
  nominalSpacing,
  tolerance,
  markerDimension,
  sessionId,
  onNominalSpacingChange,
  onToleranceChange,
  onMarkerDimensionChange,
  onSessionIdChange,
  onSubmit,
  canSubmit,
  isSubmitting,
}) => {
  const isNominalValid = !isNaN(nominalSpacing) && nominalSpacing > 0;
  const isToleranceValid = !isNaN(tolerance) && tolerance >= 0;
  const isMarkerValid = !isNaN(markerDimension) && markerDimension > 0;

  const applyPreset = (p: Preset) => {
    onNominalSpacingChange(p.nominal);
    onToleranceChange(p.tolerance);
    onMarkerDimensionChange(p.marker);
  };

  return (
    <div className="space-y-5 bg-surface border border-border rounded-lg p-5">
      <div className="flex items-center justify-between pb-3 border-b border-border/80">
        <div className="flex items-center gap-2 text-brand-text font-semibold text-sm">
          <Sliders className="w-4 h-4 text-brand-primary" />
          <span>Inspection Parameters & Calibration</span>
        </div>
        <span className="text-xs text-brand-muted font-mono">Metric Units (mm)</span>
      </div>

      {/* Preset Buttons */}
      <div className="space-y-1.5">
        <label className="text-xs text-brand-muted flex items-center gap-1.5 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-brand-info" />
          <span>Specification Presets</span>
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {PRESETS.map((preset) => {
            const isSelected =
              nominalSpacing === preset.nominal &&
              tolerance === preset.tolerance &&
              markerDimension === preset.marker;

            return (
              <button
                key={preset.label}
                type="button"
                onClick={() => applyPreset(preset)}
                className={`px-2.5 py-2 rounded text-left border transition-all text-xs ${
                  isSelected
                    ? 'border-brand-primary bg-brand-primary/10 text-brand-primary font-medium'
                    : 'border-border bg-surface-raised/60 hover:bg-surface-raised text-brand-muted hover:text-brand-text'
                }`}
                title={preset.description}
              >
                <div className="font-semibold truncate">{preset.label}</div>
                <div className="text-[11px] text-brand-muted font-mono">
                  {preset.nominal}mm (±{preset.tolerance}mm)
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Parameter Inputs Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Nominal Spacing */}
        <div>
          <label
            htmlFor="nominal-spacing-input"
            className="block text-xs font-medium text-brand-muted mb-1.5"
          >
            Nominal Spacing (<span className="font-mono text-brand-text">Snom</span>)
          </label>
          <div className="relative">
            <input
              id="nominal-spacing-input"
              type="number"
              step="any"
              min="1"
              value={nominalSpacing || ''}
              onChange={(e) => onNominalSpacingChange(parseFloat(e.target.value) || 0)}
              className={`w-full bg-surface-raised border rounded px-3 py-2 text-sm font-mono text-brand-text focus:outline-none transition-colors ${
                !isNominalValid ? 'border-brand-danger focus:border-brand-danger' : 'border-border focus:border-brand-primary'
              }`}
              placeholder="e.g. 200"
              aria-invalid={!isNominalValid}
            />
            <span className="absolute right-3 top-2.5 text-xs text-brand-muted font-mono pointer-events-none">
              mm
            </span>
          </div>
          {!isNominalValid && (
            <p className="text-[11px] text-brand-danger mt-1">Must be &gt; 0 mm</p>
          )}
        </div>

        {/* Tolerance */}
        <div>
          <label
            htmlFor="tolerance-input"
            className="block text-xs font-medium text-brand-muted mb-1.5"
          >
            Tolerance (<span className="font-mono text-brand-text">±T</span>)
          </label>
          <div className="relative">
            <input
              id="tolerance-input"
              type="number"
              step="any"
              min="0"
              value={tolerance >= 0 ? tolerance : ''}
              onChange={(e) => onToleranceChange(parseFloat(e.target.value) || 0)}
              className={`w-full bg-surface-raised border rounded px-3 py-2 text-sm font-mono text-brand-text focus:outline-none transition-colors ${
                !isToleranceValid ? 'border-brand-danger focus:border-brand-danger' : 'border-border focus:border-brand-primary'
              }`}
              placeholder="e.g. 15"
              aria-invalid={!isToleranceValid}
            />
            <span className="absolute right-3 top-2.5 text-xs text-brand-muted font-mono pointer-events-none">
              ± mm
            </span>
          </div>
          {!isToleranceValid && (
            <p className="text-[11px] text-brand-danger mt-1">Must be ≥ 0 mm</p>
          )}
        </div>

        {/* Marker Dimension */}
        <div>
          <label
            htmlFor="marker-dimension-input"
            className="block text-xs font-medium text-brand-muted mb-1.5"
          >
            Marker Size (<span className="font-mono text-brand-text">ArUco</span>)
          </label>
          <div className="relative">
            <input
              id="marker-dimension-input"
              type="number"
              step="any"
              min="1"
              value={markerDimension || ''}
              onChange={(e) => onMarkerDimensionChange(parseFloat(e.target.value) || 0)}
              className={`w-full bg-surface-raised border rounded px-3 py-2 text-sm font-mono text-brand-text focus:outline-none transition-colors ${
                !isMarkerValid ? 'border-brand-danger focus:border-brand-danger' : 'border-border focus:border-brand-primary'
              }`}
              placeholder="e.g. 100"
              aria-invalid={!isMarkerValid}
            />
            <span className="absolute right-3 top-2.5 text-xs text-brand-muted font-mono pointer-events-none">
              mm
            </span>
          </div>
          {!isMarkerValid && (
            <p className="text-[11px] text-brand-danger mt-1">Must be &gt; 0 mm</p>
          )}
        </div>
      </div>

      {/* Optional Session / Grid ID */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-2 border-t border-border/60">
        <div className="flex-1 max-w-sm">
          <label
            htmlFor="session-id-input"
            className="block text-xs font-medium text-brand-muted mb-1"
          >
            Session / Rebar Grid Identifier <span className="text-brand-muted/70">(Optional)</span>
          </label>
          <input
            id="session-id-input"
            type="text"
            value={sessionId}
            onChange={(e) => onSessionIdChange(e.target.value)}
            className="w-full bg-surface-raised border border-border rounded px-3 py-1.5 text-xs font-mono text-brand-text focus:border-brand-primary focus:outline-none"
            placeholder="e.g. SLAB-BAY-4B"
          />
        </div>

        {/* Submit Execution Button */}
        <div className="sm:self-end">
          <button
            type="button"
            onClick={onSubmit}
            disabled={!canSubmit || isSubmitting}
            className={`w-full sm:w-auto px-6 py-2.5 rounded-md font-semibold text-sm transition-all flex items-center justify-center gap-2 ${
              canSubmit && !isSubmitting
                ? 'bg-brand-primary text-brand-primary-foreground hover:bg-brand-primary/90 shadow-md shadow-brand-primary/10 active:scale-[0.98]'
                : 'bg-surface-raised text-brand-muted border border-border cursor-not-allowed opacity-60'
            }`}
          >
            {isSubmitting ? (
              <>
                <Crosshair className="w-4 h-4 animate-spin text-brand-primary" />
                <span>Running OpenCV 5 Pipeline...</span>
              </>
            ) : (
              <>
                <span>Analyze Grid</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
