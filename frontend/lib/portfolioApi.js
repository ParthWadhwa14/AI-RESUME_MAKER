import { createClient } from '@/lib/supabase';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getAuthHeaders() {
  const supabase = createClient();
  if (!supabase) return {};
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) return {};
  return { Authorization: `Bearer ${session.access_token}` };
}

export async function savePortfolio({ title, prompt, resumeData, files, jobId }) {
  const headers = await getAuthHeaders();
  if (!headers.Authorization) throw new Error('Not authenticated');

  const res = await fetch(`${API_URL}/api/portfolios/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({
      title: title || 'Untitled Portfolio',
      prompt: prompt || null,
      resume_data: resumeData || null,
      files,
      job_id: jobId || null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to save portfolio');
  }
  return res.json();
}

export async function listPortfolios() {
  const headers = await getAuthHeaders();
  if (!headers.Authorization) throw new Error('Not authenticated');

  const res = await fetch(`${API_URL}/api/portfolios/`, {
    headers,
  });

  if (!res.ok) throw new Error('Failed to fetch portfolios');
  return res.json();
}

export async function getPortfolio(id) {
  const headers = await getAuthHeaders();
  if (!headers.Authorization) throw new Error('Not authenticated');

  const res = await fetch(`${API_URL}/api/portfolios/${id}`, {
    headers,
  });

  if (!res.ok) throw new Error('Portfolio not found');
  return res.json();
}

export async function updatePortfolio(id, { title, files }) {
  const headers = await getAuthHeaders();
  if (!headers.Authorization) throw new Error('Not authenticated');

  const body = {};
  if (title !== undefined) body.title = title;
  if (files !== undefined) body.files = files;

  const res = await fetch(`${API_URL}/api/portfolios/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error('Failed to update portfolio');
  return res.json();
}

export async function deletePortfolio(id) {
  const headers = await getAuthHeaders();
  if (!headers.Authorization) throw new Error('Not authenticated');

  const res = await fetch(`${API_URL}/api/portfolios/${id}`, {
    method: 'DELETE',
    headers,
  });

  if (!res.ok) throw new Error('Failed to delete portfolio');
}
