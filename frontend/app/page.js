'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Cpu, Eye, Rocket, ArrowRight, Sparkles } from 'lucide-react';

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const features = [
  {
    icon: Cpu,
    title: 'AI-Orchestrated',
    description:
      'A multi-agent pipeline plans, designs, codes, and tests your portfolio — all autonomously. Seven specialized agents work in concert.',
  },
  {
    icon: Eye,
    title: 'Live Preview',
    description:
      'See your generated website running on a real dev server — full Tailwind, animations, and all dependencies working perfectly. Open it in a new tab or preview inline.',
  },
  {
    icon: Rocket,
    title: 'One-Click Deploy',
    description:
      'Deploy your portfolio directly to Vercel with a single click, or download as a ZIP to host anywhere you want.',
  },
];

export default function Home() {
  return (
    <div style={{ overflow: 'hidden' }}>
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-bg" />
        <div className="hero-glow hero-glow-1" />
        <div className="hero-glow hero-glow-2" />

        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          style={{ position: 'relative', zIndex: 1 }}
        >
          <motion.div
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--space-sm)',
              padding: '6px 16px',
              background: 'rgba(139, 92, 246, 0.1)',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.82rem',
              color: 'var(--accent-purple-light)',
              fontWeight: 500,
              marginBottom: 'var(--space-xl)',
            }}
          >
            <Sparkles size={14} />
            Powered by Multi-Agent AI
          </motion.div>

          <motion.h1
            className="hero-title gradient-text"
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
          >
            Resume Gala
          </motion.h1>

          <motion.p
            className="hero-subtitle"
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
          >
            AI-Powered Portfolio Website Generator
          </motion.p>

          <motion.p
            className="hero-description"
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
          >
            Transform your resume into a stunning, production-ready portfolio website.
            Our AI agents plan, design, code, and test — delivering a polished result
            you can preview live and deploy instantly.
          </motion.p>

          <motion.div
            className="hero-cta"
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
          >
            <Link href="/generate">
              <button className="btn-primary">
                Get Started
                <ArrowRight size={18} />
              </button>
            </Link>
            <Link href="#features">
              <button className="btn-secondary">View Demo</button>
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <p className="section-label">Features</p>
          <h2 className="section-title">
            Everything you need to build a{' '}
            <span className="gradient-text">stunning portfolio</span>
          </h2>
          <p className="section-subtitle">
            From resume data to deployed website — our AI pipeline handles it all.
          </p>
        </motion.div>

        <motion.div
          className="features-grid"
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
        >
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              className="feature-card"
              variants={fadeInUp}
              transition={{ duration: 0.5 }}
            >
              <div className="feature-icon">
                <feature.icon size={24} />
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-desc">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* How it works section */}
      <section style={{ padding: 'var(--space-4xl) var(--space-lg)' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          style={{ textAlign: 'center' }}
        >
          <p className="section-label">How It Works</p>
          <h2 className="section-title">Three simple steps</h2>
        </motion.div>

        <motion.div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 'var(--space-xl)',
            maxWidth: 900,
            margin: 'var(--space-2xl) auto 0',
          }}
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
        >
          {[
            {
              step: '01',
              title: 'Input Your Resume',
              desc: 'Fill in your details or paste your resume JSON. Add a style prompt to guide the AI.',
            },
            {
              step: '02',
              title: 'AI Generates',
              desc: 'Watch as seven AI agents collaborate to build your custom portfolio in real-time.',
            },
            {
              step: '03',
              title: 'Preview & Deploy',
              desc: 'See your live website, make conversational edits, then deploy with one click.',
            },
          ].map((item) => (
            <motion.div
              key={item.step}
              variants={fadeInUp}
              transition={{ duration: 0.5 }}
              style={{ textAlign: 'center' }}
            >
              <div
                style={{
                  fontSize: '2.5rem',
                  fontWeight: 700,
                  background: 'var(--gradient-primary)',
                  WebkitBackgroundClip: 'text',
                  backgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  marginBottom: 'var(--space-md)',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                {item.step}
              </div>
              <h3
                style={{
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  marginBottom: 'var(--space-sm)',
                }}
              >
                {item.title}
              </h3>
              <p
                style={{
                  fontSize: '0.9rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.6,
                }}
              >
                {item.desc}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* CTA Section */}
      <section
        style={{
          padding: 'var(--space-4xl) var(--space-lg)',
          textAlign: 'center',
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="card-static"
          style={{
            maxWidth: 700,
            margin: '0 auto',
            padding: 'var(--space-3xl)',
            background: 'var(--gradient-subtle)',
            borderColor: 'rgba(139, 92, 246, 0.2)',
            textAlign: 'center',
          }}
        >
          <h2
            style={{
              fontSize: '1.8rem',
              fontWeight: 700,
              marginBottom: 'var(--space-md)',
            }}
          >
            Ready to build your{' '}
            <span className="gradient-text">dream portfolio</span>?
          </h2>
          <p
            style={{
              color: 'var(--text-secondary)',
              marginBottom: 'var(--space-xl)',
              fontSize: '1rem',
            }}
          >
            It takes less than a minute. Just fill in your details and let AI do the rest.
          </p>
          <Link href="/generate">
            <button className="btn-primary" style={{ fontSize: '1rem', padding: '14px 36px' }}>
              Start Building Now
              <ArrowRight size={18} />
            </button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>
          Built with ❤️ by{' '}
          <a href="https://github.com" target="_blank" rel="noopener noreferrer">
            Resume Gala
          </a>{' '}
          · Powered by AI Multi-Agent Pipeline
        </p>
      </footer>
    </div>
  );
}
