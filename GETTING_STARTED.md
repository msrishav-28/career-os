# Getting Started

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-green?style=for-the-badge&logo=node.js&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=for-the-badge&logo=docker&logoColor=white)

This guide details the steps to set up CareerOS locally for development and testing.

## Prerequisites

Ensure the following tools are installed:

*   **Python 3.10+**: [python.org](https://python.org)
*   **Node.js 18+**: [nodejs.org](https://nodejs.org)
*   **Git**: [git-scm.com](https://git-scm.com)
*   **Docker** (Optional, for containerized setup)

## API Keys & Accounts

1.  **OpenAI API Key**: Required for AI agents. Sign up at [platform.openai.com](https://platform.openai.com).
2.  **Neon Account**: Required for the PostgreSQL database. Create a project at [neon.tech](https://neon.tech) and copy the connection string.
3.  **Auth.js Provider**: Configure Email (SMTP) and/or GitHub OAuth for sign-in.

## Installation Steps

### 1. Database Setup

CareerOS uses **Alembic migrations**.

- Local: run Postgres via `docker-compose.yml`
- Production: point `DATABASE_URL` to Neon

Apply migrations:

```bash
cd backend
alembic upgrade head
```

### 2. Backend Setup

```bash
# Clone the repository
git clone https://github.com/msrishav-28/career-os.git
cd career-os/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
```

Edit the `.env` file with your credentials:
```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
SECRET_KEY=...
```

**Start the Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup

Open a new terminal window:

```bash
cd career-os/frontend

# Install dependencies
npm install

# Configure Environment
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://...
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=...
GITHUB_ID=...
GITHUB_SECRET=...
EMAIL_SERVER=smtp://...
EMAIL_FROM=...
```

**Start the Frontend:**
```bash
npm run dev
```
The application will be available at `http://localhost:3000`.

## Verification

To verify the setup is working:

1.  **Frontend**: Open `http://localhost:3000`. The dashboard should load.
2.  **API**: Open `http://localhost:8000/docs`. You should see the Swagger UI.
3.  **Database**: Verify rows exist in Postgres after creating data in the app.

## Troubleshooting

*   **Connection Refused**: Ensure the backend is running on port 8000.
*   **Database Error**: Verify `DATABASE_URL` is correct and IP access is allowed in Supabase settings.
*   **OpenAI Error**: Check if your API key has available credits.
