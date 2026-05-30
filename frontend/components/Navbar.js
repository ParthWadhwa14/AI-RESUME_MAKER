'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { createClient } from '@/lib/supabase';
import { Sparkles, LogOut, Pencil } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const { user, signOut, loading } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState('');
  const [savingName, setSavingName] = useState(false);
  const [nameError, setNameError] = useState('');
  const menuRef = useRef(null);

  const displayName = user?.user_metadata?.full_name || '';
  const email = user?.email || '';

  useEffect(() => {
    const onClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  const handleSaveName = async () => {
    const nextName = nameInput.trim();
    if (!nextName) {
      setNameError('Name cannot be empty.');
      return;
    }
    setSavingName(true);
    setNameError('');
    try {
      const supabase = createClient();
      if (!supabase) throw new Error('Supabase is not configured.');
      const { error } = await supabase.auth.updateUser({
        data: { full_name: nextName },
      });
      if (error) throw error;
      setEditingName(false);
    } catch (err) {
      setNameError(err?.message || 'Failed to update name.');
    } finally {
      setSavingName(false);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link href="/" className="navbar-logo">
          <Sparkles size={18} style={{ display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
          Resume Gala
        </Link>

        <div className="navbar-links">
          {!loading && user ? (
            <>
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
              <div style={{ position: 'relative' }} ref={menuRef}>
                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen((prev) => !prev);
                    setEditingName(false);
                    setNameInput(displayName || '');
                    setNameError('');
                  }}
                  style={{ background: 'none', border: 'none', padding: 0 }}
                  title="Profile menu"
                >
                  {user.user_metadata?.avatar_url ? (
                    <div className="navbar-avatar">
                      <img
                        src={user.user_metadata.avatar_url}
                        alt={user.user_metadata.full_name || 'User'}
                      />
                    </div>
                  ) : (
                    <div
                      className="navbar-avatar"
                      style={{
                        background: 'var(--gradient-primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color: 'white',
                      }}
                    >
                      {(user.email || 'U')[0].toUpperCase()}
                    </div>
                  )}
                </button>

                {menuOpen ? (
                  <div
                    className="glass"
                    style={{
                      position: 'absolute',
                      right: 0,
                      top: 'calc(100% + 8px)',
                      minWidth: 260,
                      padding: '12px',
                      zIndex: 1200,
                    }}
                  >
                    {!editingName ? (
                      <>
                        <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>
                          {displayName || 'Name not set'}
                        </div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', marginTop: 2 }}>
                          {email || 'No email'}
                        </div>
                        <button
                          type="button"
                          className="btn-secondary btn-small"
                          onClick={() => {
                            setEditingName(true);
                            setNameInput(displayName || '');
                          }}
                          style={{ marginTop: '10px', width: '100%' }}
                        >
                          <Pencil size={14} />
                          {displayName ? 'Edit Name' : 'Add Name'}
                        </button>
                      </>
                    ) : (
                      <>
                        <input
                          className="input"
                          type="text"
                          placeholder="Enter your full name"
                          value={nameInput}
                          onChange={(e) => setNameInput(e.target.value)}
                          style={{ width: '100%' }}
                        />
                        {nameError ? (
                          <div style={{ color: 'var(--accent-red)', fontSize: '0.78rem', marginTop: 6 }}>
                            {nameError}
                          </div>
                        ) : null}
                        <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                          <button
                            type="button"
                            className="btn-primary btn-small"
                            onClick={handleSaveName}
                            disabled={savingName}
                            style={{ flex: 1 }}
                          >
                            {savingName ? 'Saving...' : 'Save'}
                          </button>
                          <button
                            type="button"
                            className="btn-secondary btn-small"
                            onClick={() => setEditingName(false)}
                            style={{ flex: 1 }}
                          >
                            Cancel
                          </button>
                        </div>
                      </>
                    )}
                    <button
                      onClick={signOut}
                      className="btn-icon"
                      title="Sign out"
                      style={{ width: 32, height: 32, marginTop: 10 }}
                    >
                      <LogOut size={16} />
                    </button>
                  </div>
                ) : null}
              </div>
            </>
          ) : !loading ? (
            <Link href="/login">
              <button className="btn-primary btn-small">Sign In</button>
            </Link>
          ) : null}
        </div>
      </div>
    </nav>
  );
}
