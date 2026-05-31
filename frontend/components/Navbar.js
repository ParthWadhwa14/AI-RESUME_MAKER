'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sparkles } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link href="/" className="navbar-logo">
          <Sparkles size={18} style={{ display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
          Resume Gala
        </Link>

        <div className="navbar-links">
          <Link
            href="/dashboard"
            className={`navbar-link ${pathname === '/dashboard' ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link
            href="/generate"
            className={`navbar-link ${pathname === '/generate' ? 'active' : ''}`}
          >
            Generate
          </Link>
        </div>
      </div>
    </nav>
  );
}
