import React, { useState } from 'react';
import { Terminal, Copy, Check, ChevronDown, ChevronRight, Clock, Code } from 'lucide-react';
import { TraceStep } from '../types/api';

interface AgentTraceTimelineProps {
  trace: TraceStep[];
  traceId: string;
}

export const AgentTraceTimeline: React.FC<AgentTraceTimelineProps> = ({ trace, traceId }) => {
  const [copied, setCopied] = useState(false);
  const [expandedStep, setExpandedStep] = useState<number | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(trace, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const totalDurationMs = trace.reduce((acc, step) => acc + (step.duration_ms || 0), 0);

  return (
    <div className="bg-surface border border-border rounded-lg overflow-hidden space-y-0">
      {/* Header bar */}
      <div className="px-4 py-3 border-b border-border flex items-center justify-between bg-surface-raised/40">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-brand-primary" />
          <span className="text-sm font-semibold text-brand-text">
            Agentic Computer Vision Execution Trace
          </span>
          <span className="text-xs font-mono text-brand-muted hidden sm:inline">
            (OpenCV 5 Deterministic Controller)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs font-mono text-brand-muted mr-1">
            <Clock className="w-3.5 h-3.5" />
            <span>{totalDurationMs.toFixed(1)} ms total</span>
          </div>

          <button
            type="button"
            onClick={() => setShowRawJson(!showRawJson)}
            className="px-2.5 py-1 rounded border border-border hover:bg-surface-raised text-xs text-brand-muted hover:text-brand-text transition-colors flex items-center gap-1 font-mono"
            title="Toggle raw JSON payload"
          >
            <Code className="w-3 h-3" />
            <span>{showRawJson ? 'Timeline' : 'Raw JSON'}</span>
          </button>

          <button
            type="button"
            onClick={handleCopy}
            className="px-2.5 py-1 rounded border border-border hover:bg-surface-raised text-xs text-brand-muted hover:text-brand-text transition-colors flex items-center gap-1"
            title="Copy trace JSON to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-brand-success" />
                <span className="text-brand-success">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {showRawJson ? (
        <div className="p-4 bg-background max-h-96 overflow-auto">
          <pre className="text-[11px] font-mono text-brand-text whitespace-pre-wrap">
            {JSON.stringify(trace, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="p-4 space-y-2">
          <div className="text-xs font-mono text-brand-muted mb-3 flex items-center justify-between">
            <span>Trace Session ID: {traceId}</span>
            <span>{trace.length} tool stages executed</span>
          </div>

          <div className="space-y-2">
            {trace.map((step) => {
              const isExpanded = expandedStep === step.step_index;
              const isSuccess =
                step.output_status === 'ok' ||
                step.output_status === 'passed' ||
                step.output_status === 'measured' ||
                step.output_status === 'success';

              return (
                <div
                  key={step.step_index}
                  className="border border-border/70 rounded-md bg-surface-raised/40 overflow-hidden text-xs"
                >
                  <button
                    type="button"
                    onClick={() => setExpandedStep(isExpanded ? null : step.step_index)}
                    className="w-full px-3.5 py-2.5 flex items-center justify-between text-left hover:bg-surface-raised/80 transition-colors"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="font-mono text-brand-muted text-[11px]">
                        #{step.step_index}
                      </span>
                      <span className="font-mono font-semibold text-brand-text truncate">
                        {step.tool}
                      </span>
                      {step.reason_code && (
                        <span className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-surface border border-border text-[10px] font-mono text-brand-muted">
                          {step.reason_code}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span className="font-mono text-[11px] text-brand-muted">
                        {step.duration_ms.toFixed(1)}ms
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                          isSuccess
                            ? 'bg-brand-success/15 text-brand-success border border-brand-success/30'
                            : 'bg-brand-warning/15 text-brand-warning border border-brand-warning/30'
                        }`}
                      >
                        {step.output_status}
                      </span>
                      {isExpanded ? (
                        <ChevronDown className="w-3.5 h-3.5 text-brand-muted" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5 text-brand-muted" />
                      )}
                    </div>
                  </button>

                  {/* Expanded Step Details */}
                  {isExpanded && (
                    <div className="p-3 border-t border-border/60 bg-background/50 space-y-2 text-[11px] font-mono">
                      <div>
                        <div className="text-brand-muted font-sans font-medium mb-1">Inputs:</div>
                        <pre className="p-2 rounded bg-surface border border-border/60 text-brand-text overflow-x-auto">
                          {JSON.stringify(step.inputs_summary, null, 2)}
                        </pre>
                      </div>

                      {step.details && (
                        <div>
                          <div className="text-brand-muted font-sans font-medium mb-1">
                            Outputs / Metrics:
                          </div>
                          <pre className="p-2 rounded bg-surface border border-border/60 text-brand-text overflow-x-auto">
                            {JSON.stringify(step.details, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
