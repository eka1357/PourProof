import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ImageUpload } from '../components/ImageUpload';

describe('ImageUpload', () => {
  it('renders dropzone when no file is selected', () => {
    render(<ImageUpload selectedFile={null} onFileSelect={vi.fn()} />);

    expect(
      screen.getByText(/Drop inspection image here or/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Max 25 MB · JPEG, PNG, WebP/i)).toBeInTheDocument();
  });

  it('accepts and notifies on valid image file selection', () => {
    const handleFileSelect = vi.fn();
    render(<ImageUpload selectedFile={null} onFileSelect={handleFileSelect} />);

    const file = new File(['valid-image-bytes'], 'rebar_mat.jpg', { type: 'image/jpeg' });
    const input = screen.getByLabelText(/Upload rebar grid photograph/i);

    fireEvent.change(input, { target: { files: [file] } });

    expect(handleFileSelect).toHaveBeenCalledWith(file);
  });

  it('rejects unsupported file type with error alert', () => {
    const handleFileSelect = vi.fn();
    render(<ImageUpload selectedFile={null} onFileSelect={handleFileSelect} />);

    const invalidFile = new File(['text'], 'blueprint.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Upload rebar grid photograph/i);

    fireEvent.change(input, { target: { files: [invalidFile] } });

    expect(handleFileSelect).not.toHaveBeenCalled();
    expect(screen.getByText(/Unsupported format/i)).toBeInTheDocument();
  });

  it('rejects files larger than 25 MB', () => {
    const handleFileSelect = vi.fn();
    render(<ImageUpload selectedFile={null} onFileSelect={handleFileSelect} />);

    // Create a 26 MB mock file
    const largeFile = new File([new ArrayBuffer(26 * 1024 * 1024)], 'huge_photo.png', {
      type: 'image/png',
    });
    const input = screen.getByLabelText(/Upload rebar grid photograph/i);

    fireEvent.change(input, { target: { files: [largeFile] } });

    expect(handleFileSelect).not.toHaveBeenCalled();
    expect(screen.getByText(/exceeds maximum limit of 25 MB/i)).toBeInTheDocument();
  });

  it('renders file details and replace button when file is selected', () => {
    const handleFileSelect = vi.fn();
    const file = new File(['content'], 'rebar_sample.png', { type: 'image/png' });

    render(<ImageUpload selectedFile={file} onFileSelect={handleFileSelect} />);

    expect(screen.getByText('rebar_sample.png')).toBeInTheDocument();
    const replaceBtn = screen.getByRole('button', { name: /Replace Image/i });
    expect(replaceBtn).toBeInTheDocument();

    fireEvent.click(replaceBtn);
    expect(handleFileSelect).toHaveBeenCalledWith(null);
  });
});
