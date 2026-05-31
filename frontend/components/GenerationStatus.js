'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Palette,
  Search,
  Image,
  Code2,
  ShieldCheck,
  Play,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

const STAGES = [
  { key: 'planning', label: 'Planning', icon: Brain },
  { key: 'design', label: 'Design', icon: Palette },
  { key: 'research', label: 'Research', icon: Search },
  { key: 'assets', label: 'Assets', icon: Image },
  { key: 'coding', label: 'Coding', icon: Code2 },
  { key: 'checking', label: 'Checking', icon: ShieldCheck },
  { key: 'testing', label: 'Testing', icon: Play },
];

export default function GenerationStatus({ jobId, onComplete }) {
  const [currentStage, setCurrentStage] = useState(0);
  const [status, setStatus] = useState('running');
  const [agentName, setAgentName] = useState('Initializing...');
  const [error, setError] = useState(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  useEffect(() => {
    if (!jobId) return;

    let interval;
    let stopped = false;

    const stopWithError = (message) => {
      if (stopped) return;
      stopped = true;
      setStatus('error');
      setError(message);
      if (interval) clearInterval(interval);
    };

    interval = setInterval(async () => {
      try {
        const res = await fetch(`${apiUrl}/api/generate/status/${jobId}`);
        if (!res.ok) {
          if (res.status === 404) {
            stopWithError('Job not found. The server likely restarted. Please generate again.');
            return;
          }
          throw new Error('Failed to fetch status');
        }

        const data = await res.json();

        if (typeof data.progress === 'number') {
          const derivedStage = Math.min(
            STAGES.length - 1,
            Math.max(0, Math.floor((data.progress / 100) * STAGES.length))
          );
          setCurrentStage(derivedStage);
        } else if (data.stage !== undefined) {
          setCurrentStage(data.stage);
        }
        setAgentName(data.current_agent || data.agent_name || 'Processing...');

        if (data.status === 'completed') {
          setStatus('completed');
          clearInterval(interval);
          if (data.files && onComplete) {
            onComplete(data.files);
          }
        } else if (data.status === 'failed' || data.status === 'error') {
          setStatus('error');
          setError(data.error || 'An error occurred');
          clearInterval(interval);
        }
      } catch (err) {
        // Most common case: backend not running / CORS / network error.
        const msg = String(err?.message || err);
        console.error('Status poll error:', err);
        if (msg.toLowerCase().includes('failed to fetch')) {
          stopWithError('Backend API is not reachable at ' + apiUrl + '. Start the backend server and try again.');
          return;
        }
        stopWithError('Status check failed. Please retry generation.');
      }
    }, 2000);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [jobId, apiUrl, onComplete]);

  const progress = status === 'completed'
    ? 100
    : Math.round(((currentStage + 0.5) / STAGES.length) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-static"
      style={{ padding: 'var(--space-xl)' }}
    >
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
        <h3
          style={{
            fontSize: '1.2rem',
            fontWeight: 600,
            marginBottom: 'var(--space-sm)',
          }}
        >
          {status === 'completed'
            ? '✨ Generation Complete!'
            : status === 'error'
            ? '❌ Generation Failed'
            : '🚀 Generating Your Portfolio...'}
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          {status === 'completed'
            ? 'Your website is ready for preview'
            : status === 'error'
            ? error
            : `Current Agent: ${agentName}`}
        </p>
      </div>

      {/* Progress bar */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: 'var(--space-xs)',
          }}
        >
          <span
            style={{
              fontSize: '0.78rem',
              color: 'var(--text-tertiary)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {progress}%
          </span>
          <span
            style={{
              fontSize: '0.78rem',
              color: 'var(--text-tertiary)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {currentStage + 1}/{STAGES.length}
          </span>
        </div>
        <div className="progress-bar-container">
          <motion.div
            className="progress-bar-fill"
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Pipeline */}
      <div className="pipeline">
        {STAGES.map((stage, i) => {
          const Icon = stage.icon;
          let stageStatus = 'pending';
          if (i < currentStage || status === 'completed') stageStatus = 'done';
          else if (i === currentStage && status === 'running') stageStatus = 'active';

          return (
            <div key={stage.key} style={{ display: 'flex', alignItems: 'center' }}>
              <div className="pipeline-stage">
                <motion.div
                  className={`pipeline-icon ${stageStatus}`}
                  animate={
                    stageStatus === 'active'
                      ? { scale: [1, 1.08, 1] }
                      : { scale: 1 }
                  }
                  transition={
                    stageStatus === 'active'
                      ? { duration: 1.5, repeat: Infinity }
                      : {}
                  }
                >
                  {stageStatus === 'done' ? (
                    <CheckCircle2 size={20} />
                  ) : stageStatus === 'active' ? (
                    <Loader2 size={20} className="spinning" style={{ animation: 'spin 1s linear infinite' }} />
                  ) : (
                    <Icon size={20} />
                  )}
                </motion.div>
                <span className={`pipeline-label ${stageStatus}`}>
                  {stage.label}
                </span>
              </div>
              {i < STAGES.length - 1 && (
                <div
                  className={`pipeline-connector ${
                    i < currentStage || status === 'completed'
                      ? 'done'
                      : i === currentStage && status === 'running'
                      ? 'active'
                      : ''
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
