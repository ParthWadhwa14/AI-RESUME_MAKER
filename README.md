# 🎭 Resume Gala

> **AI-Orchestrated Portfolio Website Generator** — Transform your career data into stunning, deployable React portfolios in minutes.

---

## 🏗️ Architecture

```
Resume-Website-Maker/
├── backend/
│   ├── app/                    # FastAPI REST API
│   │   ├── main.py             # App factory, CORS, middleware
│   │   ├── routes/             # API endpoints
│   │   │   ├── generate.py     # POST /api/generate, GET /api/generate/status/{id}
│   │   │   ├── edit.py         # POST /api/edit
│   │   │   └── auth.py         # Supabase auth verification
│   │   ├── services/           # Business logic
│   │   │   ├── crew_runner.py  # CrewAI pipeline wrapper
│   │   │   ├── asset_bridge.py # Logo/image downloader
│   │   │   └── zip_builder.py  # ZIP export with Vercel config
│   │   └── models/
│   │       └── schemas.py      # Pydantic request/response models
│   └── website_maker/          # CrewAI multi-agent crew
│       └── src/website_maker/
│           ├── config/
│           │   ├── agents.yaml  # 8 specialized AI agents
│           │   └── tasks.yaml   # Pipeline task definitions
│           ├── crew.py          # Crew orchestration
│           └── main.py          # CLI entry point
├── frontend/                   # Next.js 14 application
│   ├── app/
│   │   ├── page.js             # Landing page
│   │   ├── login/page.js       # Google OAuth login
│   │   ├── generate/page.js    # Generation + live preview
│   │   └── dashboard/page.js   # User's generated sites
│   └── components/
│       ├── ResumeForm.js       # Structured resume input
│       ├── SandpackPreview.js  # Live website preview
│       ├── GenerationStatus.js # Real-time pipeline progress
│       └── ChatEditor.js       # Conversational edit panel
└── main.py                     # Server launcher
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### 1. Clone & Setup Backend

```bash
# Install Python dependencies
uv sync

# Configure environment variables
cp backend/website_maker/.env.example backend/website_maker/.env
# Edit .env with your API keys (NVIDIA NIM, Supabase)

# Start the FastAPI server
python main.py
# → API running at http://localhost:8000
```

### 2. Setup Frontend

```bash
cd frontend
npm install

# Configure environment variables
cp .env.local.example .env.local
# Edit .env.local with your Supabase project URL and anon key

# Start the development server
npm run dev
# → Frontend running at http://localhost:3000
```

### 3. Configure Supabase

1. Create a [Supabase](https://supabase.com) project
2. Enable **Google OAuth** under Authentication → Providers
3. Copy your project URL and anon key into both `.env` files
4. Add `http://localhost:3000` to your Supabase redirect URLs

## 🔑 Environment Variables

### Backend (`backend/website_maker/.env`)
| Variable | Description |
|----------|-------------|
| `NVIDIA_API_KEY` | NVIDIA NIM API key for LLM inference |
| `MODEL` | CrewAI model identifier (e.g., `nvidia_nim/meta/llama-3.3-70b-instruct`) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anonymous/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (backend only) |

### Frontend (`frontend/.env.local`)
| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous/public key |
| `NEXT_PUBLIC_API_URL` | Backend API URL (default: `http://localhost:8000`) |

## 🎨 How It Works

1. **Input** → Paste your resume data + describe your dream website style
2. **AI Pipeline** → 8 specialized agents analyze, design, research, code, and test
3. **Live Preview** → See your generated website instantly in the Sandpack editor
4. **Iterate** → Chat with AI to refine colors, layouts, and content
5. **Deploy** → Download as ZIP or deploy directly to Vercel

## 🧠 The AI Agent Pipeline

| Agent | Role |
|-------|------|
| 🧭 **Planning Agent** | Architects section hierarchy & SEO strategy |
| 🎨 **Design Agent** | Generates design tokens, colors, typography |
| 🔍 **Research Agent** | Fetches GitHub stats & external metrics |
| 📦 **Asset Agent** | Maps icons, logos, and image pipelines |
| ⚡ **Coding Agent** | Synthesizes modular React components |
| 🛡️ **Checking Agent** | Static analysis & import validation |
| 🧪 **Testing Agent** | Compilation simulation & responsive checks |
| ✏️ **Editing Agent** | Surgical component patches for chat edits |

## 📦 Deployment

The generated websites include a `vercel.json` configuration for seamless deployment:

```bash
# Download the ZIP from Resume Gala
unzip my-portfolio.zip
cd my-portfolio

# Deploy to Vercel
npx vercel
```

## 📄 License

MIT License — Built with ❤️ using CrewAI, FastAPI, and Next.js.
