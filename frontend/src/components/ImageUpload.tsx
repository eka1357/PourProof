import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { UploadCloud, Image as ImageIcon, X, AlertCircle, FileCheck } from 'lucide-react';

interface ImageUploadProps {
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
  disabled?: boolean;
}

const MAX_BYTES = 25 * 1024 * 1024; // 25 MB
const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export const ImageUpload: React.FC<ImageUploadProps> = ({
  selectedFile,
  onFileSelect,
  disabled = false,
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    setValidationError(null);

    // Validate mime type or extension
    const isValidType =
      ALLOWED_MIME_TYPES.includes(file.type) ||
      /\.(jpe?g|png|webp)$/i.test(file.name);

    if (!isValidType) {
      setValidationError('Unsupported format. Please upload JPEG, PNG, or WebP images.');
      return;
    }

    if (file.size === 0) {
      setValidationError('The selected file is empty (0 bytes).');
      return;
    }

    if (file.size > MAX_BYTES) {
      const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
      setValidationError(`File size (${sizeMb} MB) exceeds maximum limit of 25 MB.`);
      return;
    }

    // Set preview
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    onFileSelect(file);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled) {
      setDragOver(true);
    }
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleClear = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setValidationError(null);
    onFileSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-brand-text flex items-center gap-2">
          <span>Rebar Grid Photograph</span>
          <span className="text-xs font-normal text-brand-muted">
            (Planar top-down view with coplanar ArUco marker)
          </span>
        </label>
        <span className="text-xs text-brand-muted font-mono">Max 25 MB · JPEG, PNG, WebP</span>
      </div>

      {!selectedFile ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !disabled && fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              if (!disabled) fileInputRef.current?.click();
            }
          }}
          className={`relative border-2 border-dashed rounded-lg p-6 sm:p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
            dragOver
              ? 'border-brand-primary bg-brand-primary/5 scale-[0.99]'
              : 'border-border hover:border-brand-primary/50 bg-surface/50 hover:bg-surface'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            onChange={handleInputChange}
            disabled={disabled}
            className="hidden"
            id="rebar-image-input"
            aria-label="Upload rebar grid photograph"
          />

          <div className="h-12 w-12 rounded-full bg-surface-raised border border-border flex items-center justify-center text-brand-muted mb-3 group-hover:text-brand-primary transition-colors">
            <UploadCloud className="w-6 h-6 text-brand-primary/80" />
          </div>

          <p className="text-sm font-medium text-brand-text">
            Drop inspection image here or <span className="text-brand-primary underline underline-offset-2">browse filesystem</span>
          </p>
          <p className="text-xs text-brand-muted mt-1 max-w-sm">
            Must contain rebar layer and calibrated ArUco fiducial marker for metric rectification.
          </p>
        </div>
      ) : (
        <div className="border border-border rounded-lg p-4 bg-surface flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3.5 w-full sm:w-auto">
            {previewUrl ? (
              <div className="relative h-16 w-16 rounded border border-border overflow-hidden bg-background flex-shrink-0">
                <img
                  src={previewUrl}
                  alt="Inspection preview"
                  className="h-full w-full object-cover"
                />
              </div>
            ) : (
              <div className="h-14 w-14 rounded border border-border bg-surface-raised flex items-center justify-center text-brand-primary flex-shrink-0">
                <ImageIcon className="w-6 h-6" />
              </div>
            )}

            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-brand-text truncate max-w-xs sm:max-w-md">
                  {selectedFile.name}
                </p>
                <FileCheck className="w-4 h-4 text-brand-success flex-shrink-0" />
              </div>
              <p className="text-xs font-mono text-brand-muted mt-0.5">
                {formatFileSize(selectedFile.size)} · {selectedFile.type || 'image'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <button
              type="button"
              onClick={handleClear}
              disabled={disabled}
              className="px-3 py-1.5 rounded border border-border hover:border-brand-danger/40 hover:bg-brand-danger/10 text-xs text-brand-muted hover:text-brand-danger transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <X className="w-3.5 h-3.5" />
              <span>Replace Image</span>
            </button>
          </div>
        </div>
      )}

      {/* Validation Error Alert */}
      {validationError && (
        <div className="flex items-start gap-2 p-3 rounded-md border border-brand-danger/30 bg-brand-danger/10 text-xs text-brand-danger">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">File Rejected</p>
            <p>{validationError}</p>
          </div>
        </div>
      )}
    </div>
  );
};
