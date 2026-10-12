import React, { useEffect, useState } from 'react';
import { Activity, ShieldAlert, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { fetchHealth } from '../api/client';
import { HealthResponse } from '../types/api';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [checking, setChecking] = useState<boolean>(false);

  const checkBackend = async () => {
    setChecking(true);
    setHealthError(null);
    try {
      const res = await fetchHealth();
      setHealth(res);
    } catch (err) {
      setHealthError(err instanceof Error ? err.message : 'Backend unreachable');
      setHealth(null);
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    checkBackend();
  }, []);

  return (
    <header className="border-b border-border bg-surface/90 backdrop-blur sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Brand and Value Prop */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-md bg-brand-primary/10 border border-brand-primary/30 flex items-center justify-center text-brand-primary font-mono font-bold text-lg">
            P
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-brand-text">PourProof</span>
              <span className="text-[11px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-surface-raised border border-border text-brand-muted">
                Vision Core v1.0
              </span>
            </div>
            <p className="text-xs text-brand-muted">
              Calibrated Rebar Grid Spacing & Tolerance Inspection Workspace
            </p>
          </div>
        </div>

        {/* Status Indicators & Advisory */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Engineering Advisory Badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-border/80 bg-surface-raised/60 text-xs text-brand-muted">
            <ShieldAlert className="w-3.5 h-3.5 text-brand-warning flex-shrink-0" />
            <span className="hidden sm:inline">Aide-mémoire:</span>
            <span>Engineer of Record retains pour authority</span>
          </div>

          {/* Backend / OpenCV 5 Liveness Status */}
          <div className="flex items-center gap-1.5">
            {health ? (
              <div
                className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-brand-success/30 bg-brand-success/10 text-xs text-brand-success font-mono"
                title={`FastAPI Service connected with OpenCV ${health.opencv_version}`}
              >
                <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                <span>OpenCV {health.opencv_version}</span>
              </div>
            ) : healthError ? (
              <div
                className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-brand-danger/30 bg-brand-danger/10 text-xs text-brand-danger font-mono"
                title={healthError}
              >
                <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                <span>API Offline</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-border bg-surface-raised text-xs text-brand-muted font-mono">
                <Activity className="w-3.5 h-3.5 animate-pulse text-brand-info" />
                <span>Checking...</span>
              </div>
            )}

            <button
              onClick={checkBackend}
              disabled={checking}
              className="p-1 rounded border border-border hover:border-brand-primary/40 hover:bg-surface-raised text-brand-muted hover:text-brand-text transition-colors disabled:opacity-50"
              title="Refresh API Connection"
              aria-label="Refresh API Connection"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${checking ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
