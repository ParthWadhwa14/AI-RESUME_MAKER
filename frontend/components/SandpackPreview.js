'use client';

import { useState, useMemo } from 'react';
import {
  SandpackProvider,
  SandpackPreview as SandpackPreviewComponent,
  SandpackCodeEditor,
} from '@codesandbox/sandpack-react';
import { Monitor, Code2, Download, Rocket } from 'lucide-react';

// Sandpack runs in-browser and cannot install arbitrary npm packages.
// Keep a small allowlist of deps that are known to work in Sandpack.
const SANDBOX_SAFE_DEPS = {
  react: '^18.2.0',
  'react-dom': '^18.2.0',
};

const BLOCKED_DEPS = [
  'next',
  'next-auth',
  '@supabase/supabase-js',
  '@supabase/ssr',
  'firebase',
  'prisma',
  'bcrypt',
  'sharp',
  'canvas',
];

function normalizeFiles(files) {
  const out = {};
  for (const [path, code] of Object.entries(files || {})) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    out[normalizedPath] = { code: typeof code === 'string' ? code : String(code) };
  }
  return out;
}

function detectEntry(files) {
  // Sandpack react template uses /App.js by default.
  // Prefer /src/App.* if present.
  const candidates = ['/src/App.jsx', '/src/App.js', '/App.jsx', '/App.js'];
  for (const c of candidates) if (files[c]) return c;
  return '/App.js';
}

function sanitizeDependencies(rawDeps) {
  const deps = { ...SANDBOX_SAFE_DEPS };
  for (const [name, version] of Object.entries(rawDeps || {})) {
    if (BLOCKED_DEPS.includes(name)) continue;
    // Only allow deps with a simple string version to reduce Sandpack failures
    if (typeof version === 'string' && version.length > 0) deps[name] = version;
  }
  return deps;
}

export default function SandpackPreview({ files, jobId }) {
  const [tab, setTab] = useState('preview');

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const { sandpackFiles, customDeps, packageWarning, entryFile } = useMemo(() => {
    if (!files || Object.keys(files).length === 0) {
      return { sandpackFiles: {}, customDeps: {}, packageWarning: '', entryFile: '/App.js' };
    }

    const transformed = normalizeFiles(files);

    let rawDeps = {};
    let warning = '';

    const rawPkg = files?.['package.json'] || files?.['/package.json'];
    if (rawPkg) {
      try {
        const pkg = JSON.parse(rawPkg);
        rawDeps = pkg.dependencies || {};
      } catch {
        warning =
          'Generated package.json was invalid JSON. Preview is running with a minimal dependency set.';
      }
    }

    const safeDeps = sanitizeDependencies(rawDeps);

    // Ensure there is at least an App entry so preview always boots.
    const entry = detectEntry(transformed);
    if (!transformed[entry]) {
      transformed['/App.js'] = {
        code: `export default function App() {\n  return (\n    <div style={{fontFamily: 'system-ui', padding: 16}}>\n      <h2>Preview not available</h2>\n      <p>The generated project did not include an <code>App</code> entry file Sandpack can run.</p>\n    </div>\n  );\n}\n`,
      };
    }

    // Some generators output index.html; Sandpack react template ignores it.
    // Keep it as info for the user, but rely on App entry.

    // Show a warning if we had to drop deps that won't run in Sandpack.
    const blockedFound = Object.keys(rawDeps || {}).filter((d) => BLOCKED_DEPS.includes(d));
    const blockedMsg = blockedFound.length
      ? ` Some dependencies were removed for in-browser preview: ${blockedFound.join(', ')}.`
      : '';

    return {
      sandpackFiles: transformed,
      customDeps: safeDeps,
      packageWarning: warning ? warning + blockedMsg : blockedMsg,
      entryFile: entry,
    };
  }, [files]);

  const handleDownload = async () => {
    if (!jobId) {
      // Fallback: create zip from files in-browser
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
    // Open Vercel deploy with a template URL
    const deployUrl = `https://vercel.com/new/clone?repository-url=https://github.com/resume-gala/generated-portfolio`;
    window.open(deployUrl, '_blank');
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
      </div>

      {/* Sandpack content */}
      {packageWarning ? (
        <div
          style={{
            padding: '8px 10px',
            fontSize: '0.8rem',
            color: 'var(--accent-orange)',
            border: '1px solid rgba(245, 158, 11, 0.4)',
            borderRadius: '8px',
            marginBottom: 10,
          }}
        >
          {packageWarning}
        </div>
      ) : null}
      <SandpackProvider
        template="react"
        files={sandpackFiles}
        customSetup={{ dependencies: { ...customDeps } }}
        theme="dark"
        options={{
          showNavigator: false,
          showTabs: false,
          editorHeight: '500px',
          externalResources: ['https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap'],
          activeFile: entryFile,
        }}
      >
        <div style={{ minHeight: 500 }}>
          {tab === 'preview' ? (
            <SandpackPreviewComponent
              style={{ height: 500 }}
              showNavigator={false}
              showRefreshButton={true}
            />
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', height: 500 }}>
              <SandpackCodeEditor
                style={{ height: 500 }}
                showTabs={true}
                showLineNumbers={true}
                wrapContent={false}
              />
              <SandpackPreviewComponent style={{ height: 500 }} showNavigator={false} />
            </div>
          )}
        </div>
      </SandpackProvider>

      {/* Toolbar */}
      <div className="preview-toolbar">
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
