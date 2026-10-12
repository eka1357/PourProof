import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export const LimitationsNotice: React.FC = () => {
  return (
    <div className="border border-border/80 rounded-lg p-4 bg-surface/60 text-xs text-brand-muted space-y-2">
      <div className="flex items-center gap-2 text-brand-text font-semibold">
        <AlertTriangle className="w-4 h-4 text-brand-warning flex-shrink-0" />
        <span>Structural Engineering Operational Limitations & Advisory</span>
      </div>
      <p className="leading-relaxed">
        PourProof provides calibrated computer vision measurements strictly for <strong>visible, planar reinforcement grids</strong> accompanied by a coplanar fiducial marker. Measurements represent top-layer center-to-center distances and do not account for non-planar curvature, hidden bottom mats, lap splices, or rebar yield strength.
      </p>
      <div className="flex items-start gap-2 pt-1 border-t border-border/60 text-[11px] text-brand-text">
        <ShieldCheck className="w-3.5 h-3.5 text-brand-primary flex-shrink-0 mt-0.5" />
        <span>
          <strong>Concrete Pour Authority:</strong> This software is an engineering aide-mémoire. The licensed Engineer of Record (EOR) or certified special inspector retains sole authority and responsibility for signing off on concrete pour operations.
        </span>
      </div>
    </div>
  );
};
