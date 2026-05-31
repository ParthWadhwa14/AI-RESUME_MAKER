'use client';

import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="container" style={{ padding: '64px 16px', textAlign: 'center' }}>
      <h1 style={{ fontSize: '1.6rem', fontWeight: 700, marginBottom: 12 }}>
        Login disabled
      </h1>
      <p style={{ color: 'var(--text-secondary)', maxWidth: 560, margin: '0 auto 24px' }}>
        This app is currently running in local-only mode. Portfolios are saved to your device
        and no account is required.
      </p>
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
        <Link href="/generate">
          <button className="btn-primary">Generate</button>
        </Link>
        <Link href="/dashboard">
          <button className="btn-secondary">Dashboard</button>
        </Link>
      </div>
    </div>
  );
}
