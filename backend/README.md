# CareerOS Backend

AI-powered career acceleration system backend built with FastAPI, CrewAI, and multi-agent orchestration.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o-mini
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Secret key for JWT (generate with `openssl rand -hex 32`)

### 3. Setup Database

Run the SQL script in your Supabase SQL editor:

```bash
# Copy content from scripts/setup_db.sql
# Paste into Supabase SQL Editor and run
```

### 4. Run the Server

```bash
# Development
uvicorn api.main:app --reload --port 8000

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## Architecture

### Agents
- **Profile Agent**: Manages user profile memory using RAG
- **Discovery Agent**: Finds opportunities and contacts
- **Outreach Agent**: Generates personalized messages
- **CRM Agent**: Manages contact lifecycle
- **Growth Agent**: Provides insights and recommendations

### Crews
- **Outreach Crew**: Profile + Outreach agents for message generation
- **Discovery Crew**: Profile + Discovery agents for opportunity matching

### Services
- **ChromaDB**: Vector database for RAG
- **Supabase**: PostgreSQL for structured data
- **Redis**: Rate limiting and caching

## API Endpoints

### Profile
- `POST /api/profile/store` - Store user profile
- `GET /api/profile/query` - Query profile memory
- `GET /api/profile/{user_id}` - Get profile
- `PUT /api/profile/settings` - Update settings

### Contacts
- `POST /api/contacts` - Create contact
- `GET /api/contacts` - List contacts
- `GET /api/contacts/{id}` - Get contact
- `PUT /api/contacts/{id}` - Update contact
- `GET /api/contacts/pipeline/summary` - Pipeline stats

### Messages
- `POST /api/messages/generate` - Generate personalized message
- `POST /api/messages` - Create message
- `GET /api/messages` - List messages
- `PUT /api/messages/{id}` - Update message
- `POST /api/messages/{id}/approve` - Approve for sending
- `GET /api/messages/approval-queue` - Get approval queue

### Campaigns
- `POST /api/campaigns` - Create campaign
- `GET /api/campaigns` - List campaigns
- `PUT /api/campaigns/{id}` - Update campaign
- `GET /api/campaigns/{id}/metrics` - Campaign metrics

### Opportunities
- `POST /api/opportunities/discover` - AI discovery
- `POST /api/opportunities` - Create opportunity
- `GET /api/opportunities` - List opportunities
- `PUT /api/opportunities/{id}` - Update opportunity
- `GET /api/opportunities/top` - Top opportunities

## Development

### Run Tests
```bash
pytest
```

### Code Style
```bash
black .
flake8 .
```

## Deployment

See `../docs/deployment.md` for production deployment instructions.
