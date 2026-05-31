'use client';

import { useState, useEffect, useMemo } from 'react';
import { Monitor, Code2, Download, Rocket, ExternalLink, Loader2, RefreshCw, AlertCircle } from 'lucide-react';

/**
 * LivePreview — Replaces the old Sandpack-based preview.
 *
 * Instead of running the project in an in-browser sandbox (which can't handle
 * Tailwind, Framer Motion, etc.), this component displays an iframe pointing
 * at a real Vite dev server running on the backend.
 *
 * Props:
 *   - files: The generated file map (used for code view + download fallback)
 *   - jobId: The job ID for the generated portfolio
 *   - previewUrl: The live dev-server URL (e.g., http://localhost:5201)
 */

function CodeViewer({ files }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const fileList = useMemo(() => {
    if (!files) return [];
    return Object.keys(files)
      .filter((p) => typeof files[p] === 'string')
      .sort((a, b) => {
        // Sort src/ files first, then config, then others
        const aIsSrc = a.startsWith('src/') || a.startsWith('/src/');
        const bIsSrc = b.startsWith('src/') || b.startsWith('/src/');
        if (aIsSrc && !bIsSrc) return -1;
        if (!aIsSrc && bIsSrc) return 1;
        return a.localeCompare(b);
      });
  }, [files]);

  useEffect(() => {
    if (fileList.length > 0 && !selectedFile) {
      // Default to App.jsx or first file
      const defaultFile =
        fileList.find((f) => f.includes('App.jsx') || f.includes('App.js')) ||
        fileList[0];
      setSelectedFile(defaultFile);
    }
  }, [fileList, selectedFile]);

  if (!files || fileList.length === 0) {
    return (
      <div style={{ padding: 'var(--space-xl)', textAlign: 'center', color: 'var(--text-tertiary)' }}>
        No files to display
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', height: 500, borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border-primary)' }}>
      {/* File tree */}
      <div
        style={{
          background: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border-primary)',
          overflowY: 'auto',
          padding: 'var(--space-sm) 0',
        }}
      >
        {fileList.map((path) => (
          <button
            key={path}
            onClick={() => setSelectedFile(path)}
            style={{
              display: 'block',
              width: '100%',
              textAlign: 'left',
              padding: '6px 12px',
              fontSize: '0.78rem',
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              color: selectedFile === path ? 'var(--accent-purple-light)' : 'var(--text-secondary)',
              background: selectedFile === path ? 'rgba(139, 92, 246, 0.1)' : 'transparent',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {path.startsWith('/') ? path.slice(1) : path}
          </button>
        ))}
      </div>

      {/* Code content */}
      <div
        style={{
          background: 'var(--bg-primary)',
          overflowY: 'auto',
          padding: 'var(--space-md)',
        }}
      >
        <pre
          style={{
            margin: 0,
            fontSize: '0.82rem',
            lineHeight: 1.6,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            color: 'var(--text-primary)',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          <code>{selectedFile ? files[selectedFile] : ''}</code>
        </pre>
      </div>
    </div>
  );
}

export default function SandpackPreview({ files, jobId, previewUrl: initialPreviewUrl }) {
  const [tab, setTab] = useState('preview');
  const [previewUrl, setPreviewUrl] = useState(initialPreviewUrl || null);
  const [previewLoading, setPreviewLoading] = useState(!initialPreviewUrl);
  const [previewError, setPreviewError] = useState(null);
  const [iframeKey, setIframeKey] = useState(0);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // If we don't have a preview URL yet, poll the backend for one
  useEffect(() => {
    if (previewUrl || !jobId) return;

    let cancelled = false;
    let timer = null;
    let attempts = 0;
    const maxAttempts = 60; // 60 * 2s = 2 min max

    const poll = async () => {
      if (cancelled) return;
      attempts++;

      try {
        const res = await fetch(`${apiUrl}/api/preview/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          if (!cancelled && data.preview_url) {
            setPreviewUrl(data.preview_url);
            setPreviewLoading(false);
            return;
          }
        }
      } catch {
        // Backend might not be running or preview not ready yet
      }

      if (attempts >= maxAttempts) {
        if (!cancelled) {
          setPreviewLoading(false);
          setPreviewError('Preview server could not be started. You can still download the code and run it locally.');
        }
        return;
      }

      timer = setTimeout(poll, 2000);
    };

    setPreviewLoading(true);
    poll();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [jobId, previewUrl, apiUrl]);

  // Update if parent passes a new URL
  useEffect(() => {
    if (initialPreviewUrl && initialPreviewUrl !== previewUrl) {
      setPreviewUrl(initialPreviewUrl);
      setPreviewLoading(false);
      setPreviewError(null);
    }
  }, [initialPreviewUrl]);

  const handleDownload = async () => {
    if (!jobId) {
      alert('Download will be available when connected to the backend.');
      return;
    }
    try {
      const res = await fetch(`${apiUrl}/api/download/${jobId}`);
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume-gala-${jobId}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error:', err);
      alert('Failed to download. Please try again.');
    }
  };

  const handleDeploy = () => {
    const deployUrl = `https://vercel.com/new/clone?repository-url=https://github.com/resume-gala/generated-portfolio`;
    window.open(deployUrl, '_blank');
  };

  const handleOpenInNewTab = () => {
    if (previewUrl) {
      window.open(previewUrl, '_blank');
    }
  };

  const handleRefreshPreview = () => {
    setIframeKey((k) => k + 1);
  };

  if (!files || Object.keys(files).length === 0) {
    return (
      <div
        className="card-static"
        style={{
          padding: 'var(--space-3xl)',
          textAlign: 'center',
          color: 'var(--text-tertiary)',
        }}
      >
        <Monitor size={48} style={{ marginBottom: 'var(--space-md)', opacity: 0.3 }} />
        <p>No preview available yet</p>
      </div>
    );
  }

  return (
    <div className="preview-container">
      {/* Tab bar */}
      <div className="preview-tabs">
        <button
          className={`preview-tab ${tab === 'preview' ? 'active' : ''}`}
          onClick={() => setTab('preview')}
        >
          <Monitor size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
          Preview
        </button>
        <button
          className={`preview-tab ${tab === 'code' ? 'active' : ''}`}
          onClick={() => setTab('code')}
        >
          <Code2 size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
          Code
        </button>

        {/* Right-aligned actions in tab bar */}
        {previewUrl && tab === 'preview' && (
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 'var(--space-xs)' }}>
            <button
              onClick={handleRefreshPreview}
              title="Refresh preview"
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                padding: '4px 8px',
                borderRadius: 6,
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                fontSize: '0.8rem',
                transition: 'color 0.15s',
              }}
            >
              <RefreshCw size={13} />
            </button>
            <button
              onClick={handleOpenInNewTab}
              title="Open in new tab"
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                padding: '4px 8px',
                borderRadius: 6,
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                fontSize: '0.8rem',
                transition: 'color 0.15s',
              }}
            >
              <ExternalLink size={13} />
              <span>Open in new tab</span>
            </button>
          </div>
        )}
      </div>

      {/* Preview URL indicator */}
      {previewUrl && tab === 'preview' && (
        <div
          style={{
            padding: '6px 12px',
            fontSize: '0.78rem',
            color: 'var(--accent-green, #22c55e)',
            background: 'rgba(34, 197, 94, 0.06)',
            border: '1px solid rgba(34, 197, 94, 0.2)',
            borderRadius: 8,
            marginBottom: 8,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-green, #22c55e)', display: 'inline-block', flexShrink: 0 }} />
          Live server running at{' '}
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'var(--accent-purple-light)', textDecoration: 'underline' }}
          >
            {previewUrl}
          </a>
        </div>
      )}

      {/* Content area */}
      <div style={{ minHeight: 500 }}>
        {tab === 'preview' ? (
          previewLoading ? (
            // Loading state
            <div
              style={{
                height: 500,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--space-md)',
                background: 'var(--bg-secondary)',
                borderRadius: 12,
                border: '1px solid var(--border-primary)',
              }}
            >
              <Loader2
                size={36}
                style={{
                  animation: 'spin 1s linear infinite',
                  color: 'var(--accent-purple-light)',
                }}
              />
              <div style={{ textAlign: 'center' }}>
                <p style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                  Booting preview server…
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
                  Installing dependencies and starting Vite dev server
                </p>
              </div>
            </div>
          ) : previewError ? (
            // Error state
            <div
              style={{
                height: 500,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--space-md)',
                background: 'var(--bg-secondary)',
                borderRadius: 12,
                border: '1px solid var(--border-primary)',
              }}
            >
              <AlertCircle size={36} style={{ color: 'var(--accent-orange, #f59e0b)' }} />
              <div style={{ textAlign: 'center', maxWidth: 400 }}>
                <p style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                  Preview unavailable
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>{previewError}</p>
              </div>
              <button
                className="btn-secondary btn-small"
                onClick={() => setTab('code')}
              >
                <Code2 size={14} />
                View Code Instead
              </button>
            </div>
          ) : previewUrl ? (
            // Live iframe preview
            <iframe
              key={iframeKey}
              src={previewUrl}
              title="Portfolio Preview"
              style={{
                width: '100%',
                height: 500,
                border: '1px solid var(--border-primary)',
                borderRadius: 12,
                background: 'white',
              }}
              sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
            />
          ) : null
        ) : (
          // Code tab
          <CodeViewer files={files} />
        )}
      </div>

      {/* Toolbar */}
      <div className="preview-toolbar">
        {previewUrl && (
          <button className="btn-secondary btn-small" onClick={handleOpenInNewTab}>
            <ExternalLink size={14} />
            Open in New Tab
          </button>
        )}
        <button className="btn-secondary btn-small" onClick={handleDownload}>
          <Download size={14} />
          Download ZIP
        </button>
        <button className="btn-primary btn-small" onClick={handleDeploy}>
          <Rocket size={14} />
          Deploy to Vercel
        </button>
      </div>
    </div>
  );
}
