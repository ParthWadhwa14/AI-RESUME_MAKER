'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  Plus,
  X,
  User,
  Briefcase,
  GraduationCap,
  Code2,
  FolderOpen,
  FileJson,
  FormInput,
  Upload,
} from 'lucide-react';

const defaultResume = {
  personal: { name: '', title: '', social: { github: '', linkedin: '' } },
  education: [],
  experience: [],
  skills: [],
  projects: [],
};

function CollapsibleSection({ title, icon: Icon, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div style={{ marginBottom: 'var(--space-md)' }}>
      <div className="collapsible-header" onClick={() => setOpen(!open)}>
        <span className="collapsible-title">
          <Icon size={16} />
          {title}
        </span>
        <span className={`collapsible-toggle ${open ? 'open' : ''}`}>
          <ChevronDown size={16} />
        </span>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            style={{ overflow: 'hidden' }}
          >
            <div className="collapsible-body">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function TagsInput({ tags = [], onChange, placeholder = 'Type and press Enter...' }) {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && input.trim()) {
      e.preventDefault();
      if (!tags.includes(input.trim())) {
        onChange([...tags, input.trim()]);
      }
      setInput('');
    } else if (e.key === 'Backspace' && !input && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  const removeTag = (index) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  return (
    <div className="tags-container" onClick={() => inputRef.current?.focus()}>
      {tags.map((tag, i) => (
        <span key={i} className="tag">
          {tag}
          <button type="button" className="tag-remove" onClick={() => removeTag(i)}>
            ×
          </button>
        </span>
      ))}
      <input
        ref={inputRef}
        type="text"
        className="tag-input"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={tags.length === 0 ? placeholder : ''}
      />
    </div>
  );
}

export default function ResumeForm({ value, onChange, apiUrl }) {
  const data = { ...defaultResume, ...value };
  const [viewMode, setViewMode] = useState('form');
  const [jsonText, setJsonText] = useState('');
  const [uploadMessage, setUploadMessage] = useState('');
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const resolvedApiUrl = apiUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const normalizeResume = (payload) => {
    const parsed = payload && typeof payload === 'object' ? payload : {};
    const personal = parsed.personal && typeof parsed.personal === 'object' ? parsed.personal : {};

    return {
      personal: {
        name: personal.name || parsed.name || '',
        title: personal.title || parsed.title || '',
        social: {
          github:
            (personal.social && personal.social.github) ||
            parsed.github_url ||
            '',
          linkedin:
            (personal.social && personal.social.linkedin) ||
            parsed.linkedin_url ||
            '',
        },
      },
      education: Array.isArray(parsed.education) ? parsed.education : [],
      experience: Array.isArray(parsed.experience) ? parsed.experience : [],
      skills: Array.isArray(parsed.skills) ? parsed.skills : [],
      projects: Array.isArray(parsed.projects) ? parsed.projects : [],
    };
  };

  const update = (path, val) => {
    const newData = JSON.parse(JSON.stringify(data));
    const keys = path.split('.');
    let obj = newData;
    for (let i = 0; i < keys.length - 1; i++) {
      obj = obj[keys[i]];
    }
    obj[keys[keys.length - 1]] = val;
    onChange(newData);
  };

  const switchToJson = () => {
    setJsonText(JSON.stringify(data, null, 2));
    setViewMode('json');
  };

  const switchToForm = () => {
    try {
      const parsed = JSON.parse(jsonText);
      onChange(normalizeResume(parsed));
      setUploadMessage('');
    } catch {
      setUploadMessage('Invalid JSON format. Please fix JSON and try again.');
    }
    setViewMode('form');
  };

  const applyResumeFile = async (file) => {
    if (!file) return;

    try {
      const lowerName = (file.name || '').toLowerCase();
      let normalized;

      if (lowerName.endsWith('.json')) {
        const raw = await file.text();
        const parsed = JSON.parse(raw);
        normalized = normalizeResume(parsed);
      } else if (lowerName.endsWith('.txt') || lowerName.endsWith('.pdf')) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${resolvedApiUrl}/api/resume/parse`, {
          method: 'POST',
          body: formData,
        });
        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          throw new Error(err.detail || 'Resume parsing failed');
        }
        const payload = await response.json();
        normalized = normalizeResume(payload.resume_input || {});
      } else {
        throw new Error('Unsupported format. Please upload .json, .txt, or .pdf');
      }

      onChange(normalized);
      setUploadMessage(`Loaded resume from ${file.name}`);
      if (viewMode === 'json') {
        setJsonText(JSON.stringify(normalized, null, 2));
      }
    } catch {
      setUploadMessage('Upload failed. Please upload a valid .json, .txt, or .pdf resume file.');
    }
  };

  const handleResumeUpload = async (event) => {
    const file = event.target.files?.[0];
    await applyResumeFile(file);
    event.target.value = '';
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    setIsDragActive(false);
    const file = event.dataTransfer?.files?.[0];
    await applyResumeFile(file);
  };

  const addEducation = () => {
    update('education', [
      ...data.education,
      { institution: '', degree: '', timeline: '' },
    ]);
  };

  const removeEducation = (index) => {
    update(
      'education',
      data.education.filter((_, i) => i !== index)
    );
  };

  const updateEducation = (index, field, val) => {
    const newEd = [...data.education];
    newEd[index] = { ...newEd[index], [field]: val };
    update('education', newEd);
  };

  const addExperience = () => {
    update('experience', [
      ...data.experience,
      { company: '', role: '', timeline: '', highlights: [] },
    ]);
  };

  const removeExperience = (index) => {
    update(
      'experience',
      data.experience.filter((_, i) => i !== index)
    );
  };

  const updateExperience = (index, field, val) => {
    const newExp = [...data.experience];
    newExp[index] = { ...newExp[index], [field]: val };
    update('experience', newExp);
  };

  const addProject = () => {
    update('projects', [
      ...data.projects,
      { title: '', description: '', technologies: [] },
    ]);
  };

  const removeProject = (index) => {
    update(
      'projects',
      data.projects.filter((_, i) => i !== index)
    );
  };

  const updateProject = (index, field, val) => {
    const newProj = [...data.projects];
    newProj[index] = { ...newProj[index], [field]: val };
    update('projects', newProj);
  };

  return (
    <div className="card-static" style={{ padding: 'var(--space-lg)' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--space-lg)',
        }}
      >
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Resume Data</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.txt,.pdf,application/json,text/plain,application/pdf"
            style={{ display: 'none' }}
            onChange={handleResumeUpload}
          />
          <button
            type="button"
            className="btn-secondary btn-small"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={14} />
            Upload Resume
          </button>
          <div className="view-toggle">
          <button
            type="button"
            className={`view-toggle-btn ${viewMode === 'form' ? 'active' : ''}`}
            onClick={viewMode === 'json' ? switchToForm : undefined}
          >
            <FormInput size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
            Form
          </button>
          <button
            type="button"
            className={`view-toggle-btn ${viewMode === 'json' ? 'active' : ''}`}
            onClick={viewMode === 'form' ? switchToJson : undefined}
          >
            <FileJson size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
            JSON
          </button>
          </div>
        </div>
      </div>
      {uploadMessage ? (
        <p
          style={{
            marginBottom: 'var(--space-md)',
            fontSize: '0.82rem',
            color: uploadMessage.startsWith('Upload failed') || uploadMessage.startsWith('Invalid')
              ? 'var(--accent-red)'
              : 'var(--accent-green)',
          }}
        >
          {uploadMessage}
        </p>
      ) : null}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          marginBottom: 'var(--space-md)',
          padding: '12px 14px',
          borderRadius: 'var(--radius-md)',
          border: isDragActive
            ? '1px solid var(--accent-cyan)'
            : '1px dashed var(--glass-border-hover)',
          background: isDragActive ? 'rgba(6, 182, 212, 0.08)' : 'var(--glass-bg)',
          color: 'var(--text-secondary)',
          fontSize: '0.82rem',
          transition: 'all var(--transition-fast)',
          textAlign: 'center',
        }}
      >
        Drag & drop resume (.json, .txt, .pdf) here
      </div>

      {viewMode === 'json' ? (
        <textarea
          className="json-editor"
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
          spellCheck={false}
        />
      ) : (
        <>
          {/* Personal Info */}
          <CollapsibleSection title="Personal Info" icon={User} defaultOpen={true}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                className="input"
                type="text"
                placeholder="John Doe"
                value={data.personal.name}
                onChange={(e) => update('personal.name', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Professional Title</label>
              <input
                className="input"
                type="text"
                placeholder="Full-Stack Developer"
                value={data.personal.title}
                onChange={(e) => update('personal.title', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">GitHub Profile URL</label>
              <input
                className="input"
                type="url"
                placeholder="https://github.com/your-username"
                value={data.personal?.social?.github || ''}
                onChange={(e) => update('personal.social.github', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">LinkedIn Profile URL</label>
              <input
                className="input"
                type="url"
                placeholder="https://www.linkedin.com/in/your-profile"
                value={data.personal?.social?.linkedin || ''}
                onChange={(e) => update('personal.social.linkedin', e.target.value)}
              />
            </div>
          </CollapsibleSection>

          {/* Education */}
          <CollapsibleSection title="Education" icon={GraduationCap}>
            {data.education.map((edu, i) => (
              <div key={i} className="entry-card">
                <div className="entry-card-header">
                  <span className="entry-card-number">Education #{i + 1}</span>
                  <button
                    type="button"
                    className="btn-danger btn-small"
                    onClick={() => removeEducation(i)}
                  >
                    <X size={14} /> Remove
                  </button>
                </div>
                <div className="entry-row">
                  <div className="form-group">
                    <label className="form-label">Institution</label>
                    <input
                      className="input"
                      type="text"
                      placeholder="MIT"
                      value={edu.institution}
                      onChange={(e) => updateEducation(i, 'institution', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Degree</label>
                    <input
                      className="input"
                      type="text"
                      placeholder="B.S. Computer Science"
                      value={edu.degree}
                      onChange={(e) => updateEducation(i, 'degree', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Timeline</label>
                  <input
                    className="input"
                    type="text"
                    placeholder="2018 – 2022"
                    value={edu.timeline}
                    onChange={(e) => updateEducation(i, 'timeline', e.target.value)}
                  />
                </div>
              </div>
            ))}
            <button type="button" className="add-entry-btn" onClick={addEducation}>
              <Plus size={16} /> Add Education
            </button>
          </CollapsibleSection>

          {/* Experience */}
          <CollapsibleSection title="Experience" icon={Briefcase}>
            {data.experience.map((exp, i) => (
              <div key={i} className="entry-card">
                <div className="entry-card-header">
                  <span className="entry-card-number">Experience #{i + 1}</span>
                  <button
                    type="button"
                    className="btn-danger btn-small"
                    onClick={() => removeExperience(i)}
                  >
                    <X size={14} /> Remove
                  </button>
                </div>
                <div className="entry-row">
                  <div className="form-group">
                    <label className="form-label">Company</label>
                    <input
                      className="input"
                      type="text"
                      placeholder="Google"
                      value={exp.company}
                      onChange={(e) => updateExperience(i, 'company', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Role</label>
                    <input
                      className="input"
                      type="text"
                      placeholder="Senior Engineer"
                      value={exp.role}
                      onChange={(e) => updateExperience(i, 'role', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Timeline</label>
                  <input
                    className="input"
                    type="text"
                    placeholder="2022 – Present"
                    value={exp.timeline}
                    onChange={(e) => updateExperience(i, 'timeline', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Highlights</label>
                  <TagsInput
                    tags={exp.highlights || []}
                    onChange={(tags) => updateExperience(i, 'highlights', tags)}
                    placeholder="Add highlights..."
                  />
                </div>
              </div>
            ))}
            <button type="button" className="add-entry-btn" onClick={addExperience}>
              <Plus size={16} /> Add Experience
            </button>
          </CollapsibleSection>

          {/* Skills */}
          <CollapsibleSection title="Skills" icon={Code2}>
            <TagsInput
              tags={data.skills}
              onChange={(tags) => update('skills', tags)}
              placeholder="Add skills (React, Python, etc.)..."
            />
          </CollapsibleSection>

          {/* Projects */}
          <CollapsibleSection title="Projects" icon={FolderOpen}>
            {data.projects.map((proj, i) => (
              <div key={i} className="entry-card">
                <div className="entry-card-header">
                  <span className="entry-card-number">Project #{i + 1}</span>
                  <button
                    type="button"
                    className="btn-danger btn-small"
                    onClick={() => removeProject(i)}
                  >
                    <X size={14} /> Remove
                  </button>
                </div>
                <div className="form-group">
                  <label className="form-label">Title</label>
                  <input
                    className="input"
                    type="text"
                    placeholder="AI Chat App"
                    value={proj.title}
                    onChange={(e) => updateProject(i, 'title', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea
                    className="textarea"
                    placeholder="Brief description..."
                    value={proj.description}
                    onChange={(e) => updateProject(i, 'description', e.target.value)}
                    style={{ minHeight: 70 }}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Technologies</label>
                  <TagsInput
                    tags={proj.technologies || []}
                    onChange={(tags) => updateProject(i, 'technologies', tags)}
                    placeholder="Add technologies..."
                  />
                </div>
              </div>
            ))}
            <button type="button" className="add-entry-btn" onClick={addProject}>
              <Plus size={16} /> Add Project
            </button>
          </CollapsibleSection>
        </>
      )}
    </div>
  );
}
