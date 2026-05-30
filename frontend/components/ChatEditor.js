'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, Bot, User } from 'lucide-react';

export default function ChatEditor({ files, onFilesUpdate }) {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content:
        'Your portfolio is ready! ✨ Tell me what you\'d like to change — colors, layout, content, animations — anything!',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch(`${apiUrl}/api/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          edit_prompt: userMessage,
          current_files: files,
        }),
      });

      if (!res.ok) throw new Error('Edit request failed');

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: data.message || 'Done! I\'ve updated your portfolio with the requested changes.',
        },
      ]);

      if (data.updated_files && onFilesUpdate) {
        onFilesUpdate(data.updated_files);
      }
    } catch (err) {
      console.error('Edit error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content:
            'Sorry, I couldn\'t process that edit right now. Please make sure the backend is running and try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      {/* Messages */}
      <div className="chat-messages">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`chat-bubble ${msg.role === 'user' ? 'user' : 'ai'}`}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-xs)',
                  marginBottom: 4,
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  opacity: 0.7,
                }}
              >
                {msg.role === 'ai' ? <Bot size={12} /> : <User size={12} />}
                {msg.role === 'ai' ? 'AI Editor' : 'You'}
              </div>
              {msg.content}
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="chat-bubble ai"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}
          >
            <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
            Editing your portfolio...
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="chat-input-bar">
        <input
          ref={inputRef}
          type="text"
          className="chat-input"
          placeholder="Describe what you'd like to change..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="btn-primary"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          style={{ padding: '10px 16px', minWidth: 'auto' }}
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
