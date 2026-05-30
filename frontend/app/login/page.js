'use client';

import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Sparkles, ArrowLeft, Mail } from 'lucide-react';

export default function LoginPage() {
  const { user, loading, signInWithGoogle, signInWithEmail } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailMessage, setEmailMessage] = useState('');
  const [emailError, setEmailError] = useState('');

  useEffect(() => {
    if (!loading && user) {
      router.push('/generate');
    }
  }, [user, loading, router]);

  const handleEmailSignIn = async (event) => {
    event.preventDefault();
    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setEmailError('Please enter your email address.');
      setEmailMessage('');
      return;
    }

    setEmailLoading(true);
    setEmailError('');
    setEmailMessage('');

    const { error } = await signInWithEmail(trimmedEmail);
    if (error) {
      setEmailError(error.message || 'Failed to send sign-in email.');
    } else {
      setEmailMessage('Magic link sent. Check your inbox and open the sign-in link.');
    }
    setEmailLoading(false);
  };

  return (
    <div className="login-container">
      {/* Background glows */}
      <div
        className="hero-glow hero-glow-1"
        style={{ top: '-300px', left: '-200px', opacity: 0.1 }}
      />
      <div
        className="hero-glow hero-glow-2"
        style={{ bottom: '-300px', right: '-200px', opacity: 0.1 }}
      />

      <motion.div
        className="login-card"
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, type: 'spring', damping: 20 }}
      >
        {/* Logo */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--space-sm)',
              marginBottom: 'var(--space-md)',
            }}
          >
            <Sparkles size={28} style={{ color: 'var(--accent-purple-light)' }} />
          </div>
          <h1
            className="gradient-text"
            style={{
              fontSize: '2rem',
              fontWeight: 700,
              letterSpacing: '-0.02em',
            }}
          >
            Resume Gala
          </h1>
          <p
            style={{
              color: 'var(--text-secondary)',
              marginTop: 'var(--space-sm)',
              fontSize: '0.95rem',
            }}
          >
            Sign in to get started
          </p>
        </div>

        <form onSubmit={handleEmailSignIn} style={{ width: '100%' }}>
          <label
            htmlFor="email"
            style={{
              display: 'block',
              textAlign: 'left',
              marginBottom: 'var(--space-xs)',
              fontSize: '0.85rem',
              color: 'var(--text-secondary)',
            }}
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            className="input"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: '100%' }}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={emailLoading}
            style={{ width: '100%', marginTop: 'var(--space-md)' }}
          >
            <Mail size={16} />
            {emailLoading ? 'Sending link...' : 'Continue with Email'}
          </button>
        </form>

        {emailMessage ? (
          <p style={{ marginTop: 'var(--space-sm)', color: 'var(--accent-green)', fontSize: '0.85rem' }}>
            {emailMessage}
          </p>
        ) : null}
        {emailError ? (
          <p style={{ marginTop: 'var(--space-sm)', color: 'var(--accent-red)', fontSize: '0.85rem' }}>
            {emailError}
          </p>
        ) : null}

        {/* Google Sign-In */}
        <button className="google-btn" onClick={signInWithGoogle} style={{ marginTop: 'var(--space-lg)' }}>
          <svg width="18" height="18" viewBox="0 0 48 48">
            <path
              fill="#EA4335"
              d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
            />
            <path
              fill="#4285F4"
              d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
            />
            <path
              fill="#FBBC05"
              d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
            />
            <path
              fill="#34A853"
              d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
            />
          </svg>
          Continue with Google
        </button>

        {/* Divider */}
        <div
          style={{
            margin: 'var(--space-xl) 0',
            height: 1,
            background: 'var(--glass-border)',
          }}
        />

        {/* Back link */}
        <Link
          href="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-xs)',
            color: 'var(--text-tertiary)',
            fontSize: '0.88rem',
            transition: 'color var(--transition-base)',
          }}
        >
          <ArrowLeft size={16} />
          Back to home
        </Link>
      </motion.div>
    </div>
  );
}
