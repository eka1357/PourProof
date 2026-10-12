import React, { useState } from 'react';
import {
  Header,
} from './components/Header';
import { ImageUpload } from './components/ImageUpload';
import { ParameterForm } from './components/ParameterForm';
import { StatusBanner } from './components/StatusBanner';
import { MetricsOverview } from './components/MetricsOverview';
import { InspectionViewer } from './components/InspectionViewer';
import { MeasurementTable } from './components/MeasurementTable';
import { QualityAndCalibrationCard } from './components/QualityAndCalibrationCard';
import { AgentTraceTimeline } from './components/AgentTraceTimeline';
import { LimitationsNotice } from './components/LimitationsNotice';
import { submitInspection } from './api/client';
import { InspectionResponse } from './types/api';
import { AlertCircle, Download, RotateCcw } from 'lucide-react';

export const App: React.FC = () => {
  // Input state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [nominalSpacing, setNominalSpacing] = useState<number>(200);
  const [tolerance, setTolerance] = useState<number>(15);
  const [markerDimension, setMarkerDimension] = useState<number>(100);
  const [sessionId, setSessionId] = useState<string>('');

  // Processing state
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Result state
  const [inspection, setInspection] = useState<InspectionResponse | null>(null);

  const canSubmit =
    selectedFile !== null &&
    !isNaN(nominalSpacing) &&
    nominalSpacing > 0 &&
    !isNaN(tolerance) &&
    tolerance >= 0 &&
    !isNaN(markerDimension) &&
    markerDimension > 0;

  const handleRunInspection = async () => {
    if (!canSubmit || !selectedFile) return;

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const response = await submitInspection({
        imageFile: selectedFile,
        nominalSpacingMm: nominalSpacing,
        toleranceMm: tolerance,
        calibrationMarkerMm: markerDimension,
        sessionId: sessionId || undefined,
      });
      setInspection(response);
    } catch (err) {
      setErrorMessage(
        err instanceof Error
          ? err.message
          : 'Inspection request failed. Verify that FastAPI server is running on port 8000.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setInspection(null);
    setSelectedFile(null);
    setErrorMessage(null);
  };

  const handleExportJson = () => {
    if (!inspection) return;
    const blob = new Blob([JSON.stringify(inspection, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pourproof-inspection-${inspection.inspection_id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-background text-brand-text flex flex-col">
      {/* Top Navigation */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Workspace Introduction Banner */}
        <section className="bg-surface/80 border border-border rounded-lg p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-brand-text">
              Concrete Rebar Inspection Workspace
            </h1>
            <p className="text-xs sm:text-sm text-brand-muted mt-1 max-w-3xl leading-relaxed">
              Verify planar rebar grid spacing and design tolerance using calibrated OpenCV 5 computer vision.
              Substantive ArUco fiducial rectification eliminates perspective distortion prior to centerline detection.
            </p>
          </div>
          <div className="flex items-center gap-2 self-start md:self-center">
            <span className="text-xs font-mono px-3 py-1.5 rounded bg-surface-raised border border-border text-brand-primary">
              Multi-Stage Agentic Controller
            </span>
          </div>
        </section>

        {/* Input & Upload Section */}
        <section className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Image Upload Box */}
            <div className="lg:col-span-5">
              <ImageUpload
                selectedFile={selectedFile}
                onFileSelect={(file) => {
                  setSelectedFile(file);
                  if (inspection) setInspection(null);
                }}
                disabled={isSubmitting}
              />
            </div>

            {/* Inspection Parameters Form */}
            <div className="lg:col-span-7">
              <ParameterForm
                nominalSpacing={nominalSpacing}
                tolerance={tolerance}
                markerDimension={markerDimension}
                sessionId={sessionId}
                onNominalSpacingChange={setNominalSpacing}
                onToleranceChange={setTolerance}
                onMarkerDimensionChange={setMarkerDimension}
                onSessionIdChange={setSessionId}
                onSubmit={handleRunInspection}
                canSubmit={canSubmit}
                isSubmitting={isSubmitting}
              />
            </div>
          </div>
        </section>

        {/* Processing State Notice */}
        {isSubmitting && (
          <section
            aria-live="polite"
            className="p-6 rounded-lg border border-brand-primary/30 bg-brand-primary/5 flex flex-col sm:flex-row items-center gap-4 text-center sm:text-left"
          >
            <div className="h-10 w-10 rounded-full border-2 border-brand-primary border-t-transparent animate-spin flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-brand-text">
                Executing Calibrated Computer Vision Pipeline...
              </p>
              <p className="text-xs text-brand-muted mt-0.5">
                Decoding image &rarr; Verifying OpenCV 5 runtime &rarr; Evaluating blur/brightness gate &rarr; Rectifying ArUco perspective &rarr; Detecting rebar centerlines &rarr; Calculating physical millimeter spacing
              </p>
            </div>
          </section>
        )}

        {/* API Error Box */}
        {errorMessage && (
          <section
            role="alert"
            className="p-4 rounded-lg border border-brand-danger/40 bg-brand-danger/10 flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 text-brand-danger flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-bold text-brand-danger">Inspection Execution Error</p>
              <p className="text-xs text-brand-text mt-1 font-mono">{errorMessage}</p>
              <p className="text-xs text-brand-muted mt-2">
                Ensure local FastAPI backend is active on <code className="text-brand-text">http://127.0.0.1:8000</code> with OpenCV 5 installed in the virtual environment.
              </p>
            </div>
          </section>
        )}

        {/* Results Workspace */}
        {inspection && (
          <section className="space-y-6 pt-2">
            {/* Top Bar: Official Status Banner & Action Buttons */}
            <div className="space-y-3">
              <StatusBanner inspection={inspection} />

              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-brand-muted">
                  Schema v{inspection.schema_version} · Session: {inspection.trace_id}
                </span>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleExportJson}
                    className="px-3 py-1.5 rounded border border-border hover:bg-surface-raised text-xs text-brand-text flex items-center gap-1.5 transition-colors font-mono"
                    title="Export inspection payload as JSON"
                  >
                    <Download className="w-3.5 h-3.5 text-brand-primary" />
                    <span>Export JSON</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleReset}
                    className="px-3 py-1.5 rounded border border-border hover:bg-surface-raised text-xs text-brand-muted hover:text-brand-text flex items-center gap-1.5 transition-colors"
                    title="Reset workspace for next inspection"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>New Inspection</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Metrics Overview Cards */}
            <MetricsOverview inspection={inspection} />

            {/* Evidence Viewer (Annotated image overlay) */}
            <InspectionViewer
              originalFile={selectedFile}
              annotatedImageUrl={inspection.annotated_image_url}
              inspectionId={inspection.inspection_id}
            />

            {/* Rebar Center-to-Center Spacing Table */}
            <MeasurementTable measurements={inspection.measurements} />

            {/* Quality Gate & Calibration Details */}
            <QualityAndCalibrationCard
              qualityGate={inspection.quality_gate}
              calibration={inspection.calibration}
            />

            {/* Inspectable Agent Trace */}
            <AgentTraceTimeline trace={inspection.trace} traceId={inspection.trace_id} />
          </section>
        )}

        {/* Limitations and Pour Authorization Disclaimer */}
        <section className="pt-4">
          <LimitationsNotice />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-surface/50 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-brand-muted gap-2">
          <div>
            <span>PourProof Milestone 3 · React / TypeScript / Vite / Tailwind</span>
          </div>
          <div className="font-mono text-[11px]">
            <span>FastAPI: http://127.0.0.1:8000 · OpenCV 5.0.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
