import React from 'react';
import { Table, CheckCircle2, AlertOctagon } from 'lucide-react';
import { SpacingMeasurementItem } from '../types/api';

interface MeasurementTableProps {
  measurements: SpacingMeasurementItem[];
}

export const MeasurementTable: React.FC<MeasurementTableProps> = ({ measurements }) => {
  if (!measurements || measurements.length === 0) {
    return (
      <div className="bg-surface border border-border rounded-lg p-6 text-center">
        <Table className="w-8 h-8 mx-auto text-brand-muted/40 mb-2" />
        <p className="text-sm font-medium text-brand-text">No Measurements Available</p>
        <p className="text-xs text-brand-muted mt-1 max-w-sm mx-auto">
          Physical measurements were withheld by the controller due to image quality rejection or fiducial calibration failure.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border rounded-lg overflow-hidden">
      {/* Header bar */}
      <div className="px-4 py-3 border-b border-border flex items-center justify-between bg-surface-raised/40">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-brand-primary" />
          <span className="text-sm font-semibold text-brand-text">Rebar Center-to-Center Spacing Schedule</span>
        </div>
        <span className="text-xs font-mono text-brand-muted">
          {measurements.length} {measurements.length === 1 ? 'measurement' : 'measurements'} recorded
        </span>
      </div>

      {/* Table view */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-surface-raised/70 border-b border-border text-brand-muted uppercase font-mono tracking-wider text-[11px]">
            <tr>
              <th scope="col" className="px-4 py-2.5 font-semibold">Gap ID</th>
              <th scope="col" className="px-4 py-2.5 font-semibold">Direction</th>
              <th scope="col" className="px-4 py-2.5 font-semibold">Detected Spacing</th>
              <th scope="col" className="px-4 py-2.5 font-semibold">Nominal Spec</th>
              <th scope="col" className="px-4 py-2.5 font-semibold">Deviation (Δ)</th>
              <th scope="col" className="px-4 py-2.5 font-semibold">Tolerance Conformance</th>
              <th scope="col" className="px-4 py-2.5 font-semibold">Vision Quality</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60 font-mono">
            {measurements.map((item) => {
              const formattedSpacing = item.spacing_mm !== null ? `${item.spacing_mm.toFixed(1)} mm` : '—';
              const formattedNominal = item.nominal_spacing_mm !== null ? `${item.nominal_spacing_mm.toFixed(1)} mm` : '—';
              const formattedDeviation =
                item.deviation_mm !== null
                  ? `${item.deviation_mm >= 0 ? '+' : ''}${item.deviation_mm.toFixed(1)} mm`
                  : '—';

              const directionLabel =
                item.direction === 'horizontal_spacing'
                  ? 'Horizontal'
                  : item.direction === 'vertical_spacing'
                  ? 'Vertical'
                  : item.direction;

              return (
                <tr
                  key={item.measurement_id}
                  className={`hover:bg-surface-raised/50 transition-colors ${
                    !item.in_tolerance ? 'bg-brand-danger/5' : ''
                  }`}
                >
                  {/* ID */}
                  <td className="px-4 py-3 font-semibold text-brand-text">
                    {item.measurement_id}
                  </td>

                  {/* Direction */}
                  <td className="px-4 py-3 text-brand-muted font-sans capitalize">
                    {directionLabel}
                  </td>

                  {/* Detected Spacing */}
                  <td className="px-4 py-3 font-bold text-brand-text tabular-nums">
                    {formattedSpacing}
                  </td>

                  {/* Nominal Spec */}
                  <td className="px-4 py-3 text-brand-muted tabular-nums">
                    {formattedNominal}
                  </td>

                  {/* Deviation */}
                  <td className="px-4 py-3 tabular-nums">
                    <span
                      className={`font-semibold ${
                        !item.in_tolerance
                          ? 'text-brand-danger font-bold'
                          : Math.abs(item.deviation_mm ?? 0) > (item.tolerance_mm ?? 15) * 0.75
                          ? 'text-brand-warning'
                          : 'text-brand-success'
                      }`}
                    >
                      {formattedDeviation}
                    </span>
                  </td>

                  {/* Conformance Status */}
                  <td className="px-4 py-3">
                    {item.in_tolerance ? (
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold bg-brand-success/15 text-brand-success border border-brand-success/30 font-sans">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>In Tolerance</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold bg-brand-danger/15 text-brand-danger border border-brand-danger/30 font-sans">
                        <AlertOctagon className="w-3 h-3" />
                        <span>Out of Tolerance</span>
                      </span>
                    )}
                  </td>

                  {/* Quality */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${
                        item.measurement_quality === 'high'
                          ? 'bg-brand-success/10 text-brand-success border border-brand-success/20'
                          : item.measurement_quality === 'acceptable'
                          ? 'bg-surface-raised text-brand-text border border-border'
                          : 'bg-brand-warning/15 text-brand-warning border border-brand-warning/30'
                      }`}
                    >
                      {item.measurement_quality}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
