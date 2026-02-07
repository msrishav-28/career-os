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
2.  **Supabase Account**: Required for the database. Create a new project at [supabase.com](https://supabase.com) and note the `Project URL` and `anon public` key.

## Installation Steps

### 1. Database Setup

1.  Log in to the Supabase Dashboard.
2.  Navigate to the **SQL Editor**.
3.  Execute the migration script located at `backend/scripts/setup_db.sql`.
4.  Verify that tables (users, contacts, etc.) are created.

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
SUPABASE_URL=https://...
SUPABASE_KEY=...
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
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
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
3.  **Database**: Create a profile in the app and check Supabase to confirm the data is saved.

## Troubleshooting

*   **Connection Refused**: Ensure the backend is running on port 8000.
*   **Database Error**: Verify `DATABASE_URL` is correct and IP access is allowed in Supabase settings.
*   **OpenAI Error**: Check if your API key has available credits.
