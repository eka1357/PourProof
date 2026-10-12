import React from 'react';
import { Ruler, Gauge, CheckSquare, Compass } from 'lucide-react';
import { InspectionResponse } from '../types/api';

interface MetricsOverviewProps {
  inspection: InspectionResponse;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ inspection }) => {
  const { summary, measurements, calibration } = inspection;

  const firstM = measurements.length > 0 ? measurements[0] : null;
  const nominalSpacing = firstM?.nominal_spacing_mm ?? null;
  const tolerance = firstM?.tolerance_mm ?? null;

  const meanSpacing = summary?.mean_spacing_mm ?? null;
  const maxDeviation = summary?.max_deviation_mm ?? null;
  const totalMeasured = summary?.measured_count ?? measurements.length;
  const inToleranceCount = summary?.in_tolerance_count ?? measurements.filter((m) => m.in_tolerance).length;
  const outOfToleranceCount = summary?.out_of_tolerance_count ?? measurements.filter((m) => !m.in_tolerance).length;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Mean Detected Physical Spacing */}
      <div className="bg-surface border border-border rounded-lg p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between text-brand-muted text-xs mb-1">
          <span className="font-medium">Mean Detected Spacing</span>
          <Ruler className="w-4 h-4 text-brand-primary" />
        </div>
        <div className="my-2">
          {meanSpacing !== null ? (
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold font-mono text-brand-text tabular-nums">
                {meanSpacing.toFixed(1)}
              </span>
              <span className="text-xs font-mono text-brand-muted">mm</span>
            </div>
          ) : (
            <span className="text-sm font-mono text-brand-muted italic">Not measured</span>
          )}
        </div>
        <div className="text-[11px] text-brand-muted border-t border-border/60 pt-2 flex items-center justify-between">
          <span>Nominal Spec:</span>
          <span className="font-mono text-brand-text">
            {nominalSpacing !== null ? `${nominalSpacing.toFixed(1)} mm` : '—'}
          </span>
        </div>
      </div>

      {/* 2. Max Deviation from Nominal */}
      <div className="bg-surface border border-border rounded-lg p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between text-brand-muted text-xs mb-1">
          <span className="font-medium">Max Deviation (Δ)</span>
          <Gauge className="w-4 h-4 text-brand-info" />
        </div>
        <div className="my-2">
          {maxDeviation !== null ? (
            <div className="flex items-baseline gap-1.5">
              <span
                className={`text-2xl font-bold font-mono tabular-nums ${
                  tolerance !== null && Math.abs(maxDeviation) > tolerance
                    ? 'text-brand-danger'
                    : 'text-brand-text'
                }`}
              >
                {maxDeviation >= 0 ? `+${maxDeviation.toFixed(1)}` : maxDeviation.toFixed(1)}
              </span>
              <span className="text-xs font-mono text-brand-muted">mm</span>
            </div>
          ) : (
            <span className="text-sm font-mono text-brand-muted italic">Not measured</span>
          )}
        </div>
        <div className="text-[11px] text-brand-muted border-t border-border/60 pt-2 flex items-center justify-between">
          <span>Tolerance Limit:</span>
          <span className="font-mono text-brand-text">
            {tolerance !== null ? `±${tolerance.toFixed(1)} mm` : '—'}
          </span>
        </div>
      </div>

      {/* 3. Rebar Gaps In-Tolerance */}
      <div className="bg-surface border border-border rounded-lg p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between text-brand-muted text-xs mb-1">
          <span className="font-medium">Tolerance Conformance</span>
          <CheckSquare className="w-4 h-4 text-brand-success" />
        </div>
        <div className="my-2">
          <div className="flex items-baseline gap-1.5">
            <span
              className={`text-2xl font-bold font-mono tabular-nums ${
                outOfToleranceCount > 0 ? 'text-brand-warning' : 'text-brand-success'
              }`}
            >
              {inToleranceCount} / {totalMeasured}
            </span>
            <span className="text-xs font-mono text-brand-muted">gaps</span>
          </div>
        </div>
        <div className="text-[11px] text-brand-muted border-t border-border/60 pt-2 flex items-center justify-between">
          <span>Flagged Out:</span>
          <span
            className={`font-mono font-medium ${
              outOfToleranceCount > 0 ? 'text-brand-danger' : 'text-brand-muted'
            }`}
          >
            {outOfToleranceCount} {outOfToleranceCount === 1 ? 'gap' : 'gaps'}
          </span>
        </div>
      </div>

      {/* 4. Calibration & Scale */}
      <div className="bg-surface border border-border rounded-lg p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between text-brand-muted text-xs mb-1">
          <span className="font-medium">Planar Calibration</span>
          <Compass className="w-4 h-4 text-brand-warning" />
        </div>
        <div className="my-2">
          {calibration.scale_mm_per_pixel ? (
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold font-mono text-brand-text tabular-nums">
                {calibration.scale_mm_per_pixel.toFixed(3)}
              </span>
              <span className="text-xs font-mono text-brand-muted">mm/px</span>
            </div>
          ) : (
            <span className="text-sm font-mono text-brand-danger italic">Uncalibrated</span>
          )}
        </div>
        <div className="text-[11px] text-brand-muted border-t border-border/60 pt-2 flex items-center justify-between">
          <span>Fiducial:</span>
          <span className="font-mono text-brand-text">
            {calibration.marker_id !== null ? `ArUco #${calibration.marker_id}` : 'None'}
          </span>
        </div>
      </div>
    </div>
  );
};
