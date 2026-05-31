'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { listPortfolios, deletePortfolio } from '@/lib/portfolioApi';
import {
  Plus,
  Eye,
  Trash2,
  FolderOpen,
  Calendar,
  Sparkles,
} from 'lucide-react';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
};

export default function DashboardPage() {
  const [websites, setWebsites] = useState([]);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoadError('');
        const data = await listPortfolios();
        if (!cancelled) setWebsites(data);
      } catch (err) {
        console.error('Failed to fetch portfolios:', err);
        if (!cancelled) {
          setWebsites([]);
          setLoadError(
            err?.message ||
              'Could not load local portfolios. Make sure the backend is running on http://127.0.0.1:8000.'
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this portfolio?')) return;
    try {
      await deletePortfolio(id);
      setWebsites((prev) => prev.filter((w) => w.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete portfolio. Please try again.');
    }
  };

  const displaySites = websites;

  return (
    <div className="container" style={{ paddingTop: 'var(--space-xl)', paddingBottom: 'var(--space-3xl)' }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 'var(--space-2xl)',
        }}
      >
        <div>
          <h1
            style={{
              fontSize: '1.8rem',
              fontWeight: 700,
              marginBottom: 'var(--space-xs)',
              letterSpacing: '-0.02em',
            }}
          >
            Dashboard
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Your locally saved portfolios
          </p>
          {loadError ? (
            <p style={{ color: 'var(--accent-red, #ef4444)', fontSize: '0.85rem', marginTop: 8 }}>
              {loadError}
            </p>
          ) : null}
        </div>
        <Link href="/generate">
          <button className="btn-primary">
            <Plus size={18} />
            New Portfolio
          </button>
        </Link>
      </motion.div>

      {/* Content */}
      {displaySites.length > 0 ? (
        <motion.div
          className="dashboard-grid"
          initial="initial"
          animate="animate"
          variants={{
            animate: {
              transition: { staggerChildren: 0.1 },
            },
          }}
        >
          {/* Create new card */}
          <motion.div variants={fadeInUp} transition={{ duration: 0.4 }}>
            <Link href="/generate" style={{ display: 'block' }}>
              <div className="dashboard-create-card">
                <Plus size={40} />
                <span style={{ fontWeight: 500, fontSize: '1rem' }}>Create New</span>
              </div>
            </Link>
          </motion.div>

          {/* Existing sites */}
          {displaySites.map((site) => (
            <motion.div
              key={site.id}
              variants={fadeInUp}
              transition={{ duration: 0.4 }}
            >
              <div className="dashboard-card">
                <div className="dashboard-card-preview">
                  <div
                    style={{
                      width: '100%',
                      height: '100%',
                      background: 'var(--gradient-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--text-tertiary)',
                    }}
                  >
                    <Sparkles size={32} />
                  </div>
                </div>
                <div className="dashboard-card-body">
                  <h3 className="dashboard-card-title">{site.title}</h3>
                  <p className="dashboard-card-date">
                    <Calendar
                      size={12}
                      style={{
                        display: 'inline',
                        verticalAlign: 'middle',
                        marginRight: 4,
                      }}
                    />
                    {new Date(site.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </p>
                  <div className="dashboard-card-actions">
                    <Link href={`/generate?id=${site.id}`}>
                      <button className="btn-secondary btn-small">
                        <Eye size={14} /> Preview
                      </button>
                    </Link>
                    <button
                      className="btn-secondary btn-small"
                      onClick={() => handleDelete(site.id)}
                      style={{ color: 'var(--accent-red, #ef4444)' }}
                    >
                      <Trash2 size={14} /> Delete
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        /* Empty State */
        <motion.div
          className="empty-state"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="empty-state-icon">
            <FolderOpen size={36} />
          </div>
          <h3 className="empty-state-title">No portfolios yet</h3>
          <p className="empty-state-desc">
            Create your first AI-generated portfolio website to get started.
          </p>
          <Link href="/generate">
            <button className="btn-primary">
              <Sparkles size={18} />
              Generate Your First Portfolio
            </button>
          </Link>
        </motion.div>
      )}
    </div>
  );
}
