// No Supabase for local-only mode.

// Prefer explicit NEXT_PUBLIC_API_URL, otherwise default to 127.0.0.1 (more reliable than localhost on some setups).
// If you later add a Next.js rewrite/proxy, you can set NEXT_PUBLIC_API_URL to '' and use same-origin '/api'.
const RAW_API_URL = process.env.NEXT_PUBLIC_API_URL;
const API_URL = RAW_API_URL === '' ? '' : (RAW_API_URL || 'http://127.0.0.1:8000');

export async function savePortfolio({ title, prompt, resumeData, files, jobId }) {
  const res = await fetch(`${API_URL}/api/local-portfolios/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: title || 'Untitled Portfolio',
      prompt: prompt || null,
      resume_data: resumeData || null,
      files: files || {},
      job_id: jobId || null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to save locally');
  }
  return res.json();
}

export async function listPortfolios() {
  const res = await fetch(`${API_URL}/api/local-portfolios/`);
  if (!res.ok) throw new Error('Failed to fetch local portfolios');
  return res.json();
}

export async function getPortfolio(id) {
  const res = await fetch(`${API_URL}/api/local-portfolios/${id}`);
  if (!res.ok) throw new Error('Portfolio not found');
  return res.json();
}

// Local store is immutable for now (each generated work saved as a new folder).
export async function updatePortfolio(_id, _payload) {
  throw new Error('Update is disabled in local-only mode. Save will create a new copy.');
}

export async function deletePortfolio(id) {
  const res = await fetch(`${API_URL}/api/local-portfolios/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete local portfolio');
}
