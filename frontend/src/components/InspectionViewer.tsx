import React, { useState } from 'react';
import { Eye, Layers, Maximize2, Minimize2, Image as ImageIcon, ZoomIn, ZoomOut } from 'lucide-react';
import { getAnnotatedImageUrl } from '../api/client';

interface InspectionViewerProps {
  originalFile: File | null;
  annotatedImageUrl: string | null;
  inspectionId: string;
}

type ViewMode = 'annotated' | 'original' | 'split';

export const InspectionViewer: React.FC<InspectionViewerProps> = ({
  originalFile,
  annotatedImageUrl,
  inspectionId,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('annotated');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);

  // Original image object URL
  const originalUrl = originalFile ? URL.createObjectURL(originalFile) : null;
  const annotatedSrc = annotatedImageUrl ? getAnnotatedImageUrl(annotatedImageUrl) : null;

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    setZoomLevel(1);
  };

  const zoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.25, 3));
  const zoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.25, 0.75));
  const resetZoom = () => setZoomLevel(1);

  return (
    <div
      className={`bg-surface border border-border rounded-lg flex flex-col overflow-hidden ${
        isFullscreen ? 'fixed inset-4 z-50 shadow-2xl bg-surface/95 backdrop-blur' : ''
      }`}
    >
      {/* Header bar with controls & legend */}
      <div className="px-4 py-3 border-b border-border flex flex-wrap items-center justify-between gap-3 bg-surface-raised/40">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-brand-primary" />
          <span className="text-sm font-semibold text-brand-text">Visual Evidence Inspector</span>
          <span className="text-xs font-mono text-brand-muted hidden sm:inline">
            (Inspection #{inspectionId.slice(0, 8)})
          </span>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-1.5 bg-background p-1 rounded-md border border-border">
          <button
            type="button"
            onClick={() => setViewMode('annotated')}
            disabled={!annotatedSrc}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors flex items-center gap-1.5 ${
              viewMode === 'annotated'
                ? 'bg-brand-primary text-brand-primary-foreground font-semibold shadow-sm'
                : 'text-brand-muted hover:text-brand-text'
            } disabled:opacity-40 disabled:cursor-not-allowed`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Annotated Overlay</span>
          </button>

          <button
            type="button"
            onClick={() => setViewMode('original')}
            disabled={!originalUrl}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors flex items-center gap-1.5 ${
              viewMode === 'original'
                ? 'bg-brand-primary text-brand-primary-foreground font-semibold shadow-sm'
                : 'text-brand-muted hover:text-brand-text'
            } disabled:opacity-40 disabled:cursor-not-allowed`}
          >
            <ImageIcon className="w-3.5 h-3.5" />
            <span>Original Photo</span>
          </button>

          <button
            type="button"
            onClick={() => setViewMode('split')}
            disabled={!annotatedSrc || !originalUrl}
            className={`hidden md:flex px-2.5 py-1 rounded text-xs font-medium transition-colors items-center gap-1.5 ${
              viewMode === 'split'
                ? 'bg-brand-primary text-brand-primary-foreground font-semibold shadow-sm'
                : 'text-brand-muted hover:text-brand-text'
            } disabled:opacity-40 disabled:cursor-not-allowed`}
          >
            <span>Side-by-Side</span>
          </button>
        </div>

        {/* Zoom & Fullscreen Controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={zoomOut}
            className="p-1.5 rounded border border-border hover:bg-surface-raised text-brand-muted hover:text-brand-text transition-colors"
            title="Zoom out"
            aria-label="Zoom out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={resetZoom}
            className="px-2 py-1 rounded border border-border text-[11px] font-mono text-brand-muted hover:text-brand-text hover:bg-surface-raised transition-colors"
            title="Reset zoom"
          >
            {Math.round(zoomLevel * 100)}%
          </button>
          <button
            type="button"
            onClick={zoomIn}
            className="p-1.5 rounded border border-border hover:bg-surface-raised text-brand-muted hover:text-brand-text transition-colors"
            title="Zoom in"
            aria-label="Zoom in"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={toggleFullscreen}
            className="p-1.5 rounded border border-border hover:bg-surface-raised text-brand-muted hover:text-brand-text transition-colors ml-1"
            title={isFullscreen ? 'Exit fullscreen' : 'Inspect fullscreen'}
            aria-label={isFullscreen ? 'Exit fullscreen' : 'Inspect fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Image Canvas */}
      <div className="flex-1 bg-background/80 overflow-auto p-4 flex items-center justify-center min-h-[380px] max-h-[600px] relative">
        {viewMode === 'split' && annotatedSrc && originalUrl ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full h-full items-center">
            {/* Left: Original */}
            <div className="flex flex-col items-center border border-border/80 rounded bg-surface p-2">
              <span className="text-xs font-mono text-brand-muted mb-2">Original Mat Capture</span>
              <div className="overflow-auto max-h-[500px] flex items-center justify-center">
                <img
                  src={originalUrl}
                  alt="Original Rebar Grid Capture"
                  style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
                  className="max-h-[460px] object-contain rounded transition-transform duration-100"
                />
              </div>
            </div>

            {/* Right: Annotated */}
            <div className="flex flex-col items-center border border-border/80 rounded bg-surface p-2">
              <span className="text-xs font-mono text-brand-primary mb-2">OpenCV 5 Annotated Rectification</span>
              <div className="overflow-auto max-h-[500px] flex items-center justify-center">
                <img
                  src={annotatedSrc}
                  alt="Annotated Rebar Inspection Evidence"
                  style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
                  className="max-h-[460px] object-contain rounded transition-transform duration-100"
                />
              </div>
            </div>
          </div>
        ) : viewMode === 'annotated' && annotatedSrc ? (
          <div className="overflow-auto max-h-[540px] flex items-center justify-center w-full">
            <img
              src={annotatedSrc}
              alt="Annotated Rebar Inspection Evidence"
              style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
              className="max-h-[500px] object-contain rounded shadow-lg border border-border/60 transition-transform duration-100"
            />
          </div>
        ) : originalUrl ? (
          <div className="overflow-auto max-h-[540px] flex items-center justify-center w-full">
            <img
              src={originalUrl}
              alt="Original Rebar Grid Photo"
              style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
              className="max-h-[500px] object-contain rounded shadow-lg border border-border/60 transition-transform duration-100"
            />
          </div>
        ) : (
          <div className="text-center py-12 text-brand-muted">
            <ImageIcon className="w-10 h-10 mx-auto text-brand-muted/40 mb-2" />
            <p className="text-sm">No inspection image available</p>
          </div>
        )}
      </div>

      {/* Visual Annotation Legend */}
      <div className="px-4 py-2.5 bg-surface-raised/80 border-t border-border flex flex-wrap items-center justify-between text-xs text-brand-muted gap-2">
        <span className="font-semibold text-brand-text">Annotation Legend:</span>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-cyan-400 inline-block" />
            <span>Detected Rebar Centerlines</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-2 bg-emerald-500/40 border border-emerald-400 inline-block rounded-xs" />
            <span>In-Tolerance Spacing</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-2 bg-rose-500/40 border border-rose-400 inline-block rounded-xs" />
            <span>Out-of-Tolerance Spacing</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 border border-fuchsia-400 inline-block" />
            <span>Calibrated ArUco Fiducial</span>
          </div>
        </div>
      </div>
    </div>
  );
};
