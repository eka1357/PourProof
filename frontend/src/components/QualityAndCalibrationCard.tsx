import React from 'react';
import { ShieldCheck, ShieldAlert, Crosshair, AlertCircle } from 'lucide-react';
import { QualityGateInfo, CalibrationInfo } from '../types/api';

interface QualityAndCalibrationProps {
  qualityGate: QualityGateInfo;
  calibration: CalibrationInfo;
}

export const QualityAndCalibrationCard: React.FC<QualityAndCalibrationProps> = ({
  qualityGate,
  calibration,
}) => {
  const metrics = qualityGate.metrics || {};

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* 1. OpenCV Quality Gate */}
      <div className="bg-surface border border-border rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-border/80">
          <div className="flex items-center gap-2">
            {qualityGate.accepted ? (
              <ShieldCheck className="w-4 h-4 text-brand-success" />
            ) : (
              <ShieldAlert className="w-4 h-4 text-brand-danger" />
            )}
            <span className="text-xs font-semibold text-brand-text">Image Quality Gate</span>
          </div>
          <span
            className={`text-[11px] font-mono px-2 py-0.5 rounded border uppercase font-bold ${
              qualityGate.accepted
                ? 'bg-brand-success/10 text-brand-success border-brand-success/30'
                : 'bg-brand-danger/10 text-brand-danger border-brand-danger/30'
            }`}
          >
            {qualityGate.accepted ? 'Passed' : 'Rejected'}
          </span>
        </div>

        {/* Reason Codes */}
        {qualityGate.reason_codes.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] text-brand-muted">Reason codes:</span>
            {qualityGate.reason_codes.map((code) => (
              <span
                key={code}
                className="px-1.5 py-0.5 rounded bg-surface-raised border border-border font-mono text-[10px] text-brand-text"
              >
                {code}
              </span>
            ))}
          </div>
        )}

        {/* Quality Metrics */}
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Blur Score (Laplacian)</div>
            <div className="font-bold text-brand-text mt-0.5 tabular-nums">
              {typeof metrics.blur_variance === 'number'
                ? metrics.blur_variance.toFixed(1)
                : '—'}
            </div>
          </div>

          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Mean Brightness</div>
            <div className="font-bold text-brand-text mt-0.5 tabular-nums">
              {typeof metrics.mean_brightness === 'number'
                ? `${metrics.mean_brightness.toFixed(1)} / 255`
                : '—'}
            </div>
          </div>

          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Contrast Std Dev</div>
            <div className="font-bold text-brand-text mt-0.5 tabular-nums">
              {typeof metrics.contrast_std === 'number'
                ? metrics.contrast_std.toFixed(1)
                : '—'}
            </div>
          </div>

          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Image Resolution</div>
            <div className="font-bold text-brand-text mt-0.5 tabular-nums truncate">
              {metrics.image_width && metrics.image_height
                ? `${metrics.image_width} × ${metrics.image_height}`
                : '—'}
            </div>
          </div>
        </div>
      </div>

      {/* 2. Fiducial Marker Calibration */}
      <div className="bg-surface border border-border rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-border/80">
          <div className="flex items-center gap-2">
            <Crosshair className="w-4 h-4 text-brand-primary" />
            <span className="text-xs font-semibold text-brand-text">Fiducial Calibration</span>
          </div>
          <span
            className={`text-[11px] font-mono px-2 py-0.5 rounded border uppercase font-bold ${
              calibration.valid
                ? 'bg-brand-success/10 text-brand-success border-brand-success/30'
                : 'bg-brand-danger/10 text-brand-danger border-brand-danger/30'
            }`}
          >
            {calibration.valid ? 'Calibrated' : 'Uncalibrated'}
          </span>
        </div>

        {/* Warnings */}
        {calibration.warnings.length > 0 && (
          <div className="space-y-1">
            {calibration.warnings.map((w, idx) => (
              <div
                key={idx}
                className="flex items-center gap-1.5 text-[11px] text-brand-warning bg-brand-warning/10 px-2 py-1 rounded border border-brand-warning/20"
              >
                <AlertCircle className="w-3 h-3 flex-shrink-0" />
                <span>{w}</span>
              </div>
            ))}
          </div>
        )}

        {/* Calibration Stats */}
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Scale (Physical)</div>
            <div className="font-bold text-brand-text mt-0.5 tabular-nums">
              {calibration.scale_mm_per_pixel
                ? `${calibration.scale_mm_per_pixel.toFixed(3)} mm/px`
                : '—'}
            </div>
          </div>

          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Resolution (Pixel Density)</div>
            <div className="font-bold text-brand-text mt-0.5 tabular-nums">
              {calibration.pixels_per_mm
                ? `${calibration.pixels_per_mm.toFixed(2)} px/mm`
                : '—'}
            </div>
          </div>

          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Method / Dictionary</div>
            <div className="font-bold text-brand-text mt-0.5 truncate capitalize">
              {calibration.method.replace('_', ' ')}
            </div>
          </div>

          <div className="p-2 rounded bg-surface-raised border border-border/60">
            <div className="text-[10px] text-brand-muted font-sans">Detected Marker ID</div>
            <div className="font-bold text-brand-text mt-0.5">
              {calibration.marker_id !== null ? `#${calibration.marker_id}` : 'None'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
