import React from 'react';
import {
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  HelpCircle,
  XCircle,
} from 'lucide-react';
import { InspectionResponse } from '../types/api';

interface StatusBannerProps {
  inspection: InspectionResponse;
}

export type DisplayStatusType =
  | 'Complete'
  | 'Complete with flags'
  | 'Retake image'
  | 'Needs human review'
  | 'Failed';

/**
 * Determine the official UI_UX_SPEC display status.
 * Constraint: Must strictly be one of:
 * 'Complete', 'Complete with flags', 'Retake image', 'Needs human review', 'Failed'.
 * NEVER 'PASS: SAFE'.
 */
export function deriveDisplayStatus(inspection: InspectionResponse): DisplayStatusType {
  const { status, next_action, quality_gate, calibration, summary } = inspection;

  if (status === 'processing_error' || status === 'rejected_input') {
    return 'Failed';
  }

  if (
    status === 'needs_recapture' ||
    next_action.action === 'REQUEST_RECAPTURE' ||
    !quality_gate.accepted ||
    !calibration.valid
  ) {
    return 'Retake image';
  }

  if (status === 'needs_review' || next_action.action === 'HUMAN_REVIEW') {
    return 'Needs human review';
  }

  if (status === 'measured') {
    const outCount = summary?.out_of_tolerance_count ?? 0;
    if (outCount > 0 || next_action.action === 'REVIEW_MEASUREMENT') {
      return 'Complete with flags';
    }
    return 'Complete';
  }

  return 'Needs human review';
}

const REASON_EXPLANATIONS: Record<string, { title: string; advice: string }> = {
  IN_TOLERANCE_VERIFIED: {
    title: 'All detected rebar spacings are within specified tolerance.',
    advice: 'Review visual evidence overlay and confirm grid boundaries with project drawings.',
  },
  REBAR_OUT_OF_TOLERANCE: {
    title: 'One or more rebar gaps exceed allowable spacing tolerance.',
    advice: 'Inspect flagged red spans in the measurement table. Physical adjustment of rebar is required before pour.',
  },
  ARUCO_NOT_DETECTED: {
    title: 'Coplanar calibration marker was not detected in the image.',
    advice: 'Ensure the ArUco marker is positioned on the same rebar plane, unobstructed, flat, and well-lit.',
  },
  BLUR_DETECTED: {
    title: 'Image sharpness failed blur gate (Laplacian variance below threshold).',
    advice: 'Retake photo with a stable camera position or faster shutter speed to eliminate motion blur.',
  },
  LOW_CONTRAST: {
    title: 'Image contrast is insufficient to separate rebar from background.',
    advice: 'Increase ambient lighting or adjust exposure so rebar shadows/highlights are distinct.',
  },
  TOO_DARK: {
    title: 'Image brightness is too low for reliable centerline detection.',
    advice: 'Turn on auxiliary site worklights or flash and retake the photo.',
  },
  TOO_BRIGHT: {
    title: 'Image brightness is too high with clipped highlights.',
    advice: 'Shield intense direct sunlight glare or lower camera exposure.',
  },
  INSUFFICIENT_REBARS: {
    title: 'Fewer than two parallel rebar centerlines could be detected.',
    advice: 'Ensure rebar mat spans across the center of the frame without obstruction.',
  },
  PERSPECTIVE_WARP_HIGH: {
    title: 'Camera angle is too oblique for planar rectification.',
    advice: 'Capture image closer to perpendicular (top-down 90° view over the rebar mat).',
  },
  SPACING_MEASURED: {
    title: 'Physical rebar center-to-center distances calculated.',
    advice: 'Compare detected physical spacing against contract drawings.',
  },
};

export const StatusBanner: React.FC<StatusBannerProps> = ({ inspection }) => {
  const displayStatus = deriveDisplayStatus(inspection);
  const primaryReasonCode =
    inspection.next_action.reason_code ||
    inspection.quality_gate.reason_codes[0] ||
    'STATUS_REPORTED';

  const explanation = REASON_EXPLANATIONS[primaryReasonCode] || {
    title: `Reason Code: ${primaryReasonCode}`,
    advice: 'Proceed with structural review in accordance with project inspection standards.',
  };

  const getStatusStyles = () => {
    switch (displayStatus) {
      case 'Complete':
        return {
          border: 'border-brand-success/40',
          bg: 'bg-brand-success/10',
          badge: 'bg-brand-success/20 text-brand-success border-brand-success/30',
          icon: <CheckCircle className="w-6 h-6 text-brand-success flex-shrink-0" />,
        };
      case 'Complete with flags':
        return {
          border: 'border-brand-warning/40',
          bg: 'bg-brand-warning/10',
          badge: 'bg-brand-warning/20 text-brand-warning border-brand-warning/30',
          icon: <AlertTriangle className="w-6 h-6 text-brand-warning flex-shrink-0" />,
        };
      case 'Retake image':
        return {
          border: 'border-brand-warning/50',
          bg: 'bg-brand-warning/15',
          badge: 'bg-brand-warning/20 text-brand-warning border-brand-warning/40',
          icon: <RotateCcw className="w-6 h-6 text-brand-warning flex-shrink-0" />,
        };
      case 'Needs human review':
        return {
          border: 'border-brand-info/40',
          bg: 'bg-brand-info/10',
          badge: 'bg-brand-info/20 text-brand-info border-brand-info/30',
          icon: <HelpCircle className="w-6 h-6 text-brand-info flex-shrink-0" />,
        };
      case 'Failed':
      default:
        return {
          border: 'border-brand-danger/40',
          bg: 'bg-brand-danger/10',
          badge: 'bg-brand-danger/20 text-brand-danger border-brand-danger/30',
          icon: <XCircle className="w-6 h-6 text-brand-danger flex-shrink-0" />,
        };
    }
  };

  const styles = getStatusStyles();

  return (
    <div
      role="status"
      className={`rounded-lg border p-5 ${styles.border} ${styles.bg} transition-all`}
    >
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Status Identifier and Primary Reason */}
        <div className="flex items-start gap-3.5">
          {styles.icon}
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <span
                data-testid="status-badge"
                className={`text-sm font-bold uppercase tracking-wider px-2.5 py-0.5 rounded border font-mono ${styles.badge}`}
              >
                {displayStatus}
              </span>

              {/* Next Action Pill */}
              <div className="flex items-center gap-1 text-xs font-mono text-brand-muted bg-surface-raised px-2 py-0.5 rounded border border-border">
                <span>Next Action:</span>
                <span className="text-brand-text font-semibold">
                  {inspection.next_action.action}
                </span>
              </div>

              {/* Inspection ID */}
              <span className="text-xs font-mono text-brand-muted">
                ID: {inspection.inspection_id.slice(0, 8)}
              </span>
            </div>

            <p className="text-sm font-medium text-brand-text mt-1.5">{explanation.title}</p>
            <p className="text-xs text-brand-muted mt-0.5">{explanation.advice}</p>
          </div>
        </div>

        {/* Reason Code Technical Disclosure */}
        <div className="flex flex-col items-start md:items-end gap-1 flex-shrink-0">
          <div className="flex items-center gap-1.5 text-xs text-brand-muted">
            <span>Code:</span>
            <code className="px-2 py-0.5 rounded bg-surface border border-border font-mono text-brand-text text-[11px]">
              {primaryReasonCode}
            </code>
          </div>
          {inspection.quality_gate.reason_codes.length > 1 && (
            <div className="text-[11px] text-brand-muted flex items-center gap-1">
              <span>Additional flags:</span>
              <span className="font-mono">
                {inspection.quality_gate.reason_codes.slice(1).join(', ')}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
