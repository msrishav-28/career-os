# CareerOS - AI Career Co-Pilot

**Your AI-powered career acceleration and startup validation platform**

Automate networking, outreach, and opportunity discovery while maintaining authentic human connection. Let 6 specialized AI agents handle repetitive tasks while you focus on meaningful conversations and building.

## Features

- **🤖 AI-Powered Outreach**: Generate personalized messages that score 70+ on quality
- **🎯 Smart Discovery**: Find relevant jobs, internships, and connections daily
- **📊 CRM Management**: Track contacts through complete lifecycle
- **📈 Growth Analytics**: Data-driven insights and recommendations
- **⚡ Safe Automation**: Platform-compliant rate limiting
- **🔄 Multi-Campaign Support**: Run multiple outreach campaigns simultaneously

## Tech Stack

### Backend
- **Framework**: CrewAI + FastAPI
- **AI**: GPT-4o-mini via OpenAI
- **Vector DB**: ChromaDB (RAG)
- **Database**: Supabase (PostgreSQL)
- **Queue**: Redis + Celery
- **Tools**: Selenium, BeautifulSoup, Playwright

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Animation**: Framer Motion
- **Icons**: Lucide React

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (via Supabase)
- Redis
- OpenAI API key

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Setup database (run SQL in Supabase)
# Copy scripts/setup_db.sql to Supabase SQL Editor

# Start server
uvicorn api.main:app --reload
```

Backend will run at `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

Frontend will run at `http://localhost:3000`

## Project Structure

```
CareerOS/
├── backend/
│   ├── agents/          # 6 AI agents
│   ├── crews/           # Multi-agent orchestration
│   ├── tools/           # Agent tools (LinkedIn, GitHub, Email, etc.)
│   ├── api/             # FastAPI routes
│   ├── models/          # Pydantic models
│   ├── services/        # ChromaDB, Supabase, Redis
│   └── config/          # Settings and prompts
│
├── frontend/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   ├── lib/             # API client, utilities
│   └── stores/          # State management
│
└── docs/                # Documentation
```

## Usage

### 1. Setup Your Profile

```bash
# Store your profile data
POST /api/profile/store
{
  "skills": ["Python", "Machine Learning", ...],
  "projects": [...],
  "goals": [...]
}
```

### 2. Discover Opportunities

```bash
# AI discovers and scores opportunities
POST /api/opportunities/discover
```

### 3. Generate Outreach

```bash
# Generate personalized messages
POST /api/messages/generate
{
  "contact_id": "...",
  "context": "internship application"
}
```

### 4. Approve & Send

```bash
# Review and approve messages
POST /api/messages/{id}/approve
```

## Key Metrics

- **20-30%** response rate on outreach
- **15-20** quality outreach per day
- **0** platform violations
- **10+** hours saved per week

## Safety & Compliance

- ✅ Platform rate limits enforced
- ✅ Human-in-loop approval for all messages
- ✅ Personalization score threshold (70+)
- ✅ Human-like timing and behavior
- ✅ Respects rejection signals

## Deployment

### Backend (Railway)

```bash
# Deploy to Railway
railway init
railway up
```

### Frontend (Vercel)

```bash
# Deploy to Vercel
vercel deploy
```

See `docs/deployment.md` for detailed instructions.

## Development

### Run Tests

```bash
# Backend
pytest

# Frontend
npm test
```

### Code Style

```bash
# Backend
black .
flake8 .

# Frontend
npm run lint
```

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_KEY=...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## Support

- 📧 Email: support@careeros.dev
- 🐛 Issues: GitHub Issues
- 💬 Discord: [Join our community]

---

**Built with ❤️ for ambitious professionals**
