'use client';

import { useState } from 'react';
import { MessageSquare } from 'lucide-react';

const EXAMPLE_PROMPTS = [
  'Dark minimal with glassmorphism',
  'Colorful creative portfolio',
  'Clean corporate professional',
  'Futuristic tech showcase',
];

export default function PromptInput({ value, onChange }) {
  const MAX_CHARS = 500;

  return (
    <div className="card-static" style={{ padding: 'var(--space-lg)' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)',
          marginBottom: 'var(--space-lg)',
        }}
      >
        <MessageSquare size={18} style={{ color: 'var(--accent-cyan)' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Style Prompt</h3>
      </div>

      <p
        style={{
          fontSize: '0.88rem',
          color: 'var(--text-secondary)',
          marginBottom: 'var(--space-md)',
          lineHeight: 1.6,
        }}
      >
        Describe the look and feel you want for your portfolio website. Be creative!
      </p>

      <textarea
        className="textarea"
        placeholder="Describe your ideal portfolio style... e.g., 'A sleek dark theme with purple accents, smooth animations, and a modern tech feel'"
        value={value}
        onChange={(e) => {
          if (e.target.value.length <= MAX_CHARS) {
            onChange(e.target.value);
          }
        }}
        style={{ minHeight: 140 }}
      />

      <div className="prompt-counter">
        {value.length} / {MAX_CHARS}
      </div>

      <div style={{ marginTop: 'var(--space-md)' }}>
        <span
          style={{
            fontSize: '0.78rem',
            color: 'var(--text-tertiary)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            fontWeight: 500,
          }}
        >
          Try a style:
        </span>
        <div className="prompt-chips">
          {EXAMPLE_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="prompt-chip"
              onClick={() => onChange(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
