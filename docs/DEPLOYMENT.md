# Deployment Guide

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

This document provides step-by-step instructions to deploy CareerOS to a production environment.

## Prerequisites

Ensure you have the following accounts and tools ready:

*   **GitHub Account**: To host the repository.
*   **Railway Account**: For hosting the Backend and Redis.
*   **Vercel Account**: For hosting the Frontend.
*   **Supabase Account**: For the PostgreSQL database.
*   **OpenAI API Key**: For the AI agents.

## 1. Database Setup (Supabase)

1.  **Create Project**: Log in to Supabase and create a new project.
2.  **Save Credentials**: Note down the `Project URL` and `anon public` key from the API settings. You will also need the `service_role` key (keep this secret) and your database password.
3.  **Database Migration**:
    *   Navigate to the SQL Editor in your Supabase dashboard.
    *   Open the file `backend/scripts/setup_db.sql` from this repository.
    *   Copy the entire content and paste it into the SQL Editor.
    *   Click "Run" to execute the script.
    *   **Verify**: Check the "Table Editor" to ensure tables like `users`, `contacts`, `opportunities`, etc., have been created.

## 2. Backend Deployment (Railway)

The backend is configured to run on Railway using the provided `railway.json` configuration.

1.  **Create Service**:
    *   Log in to Railway.
    *   Click "New Project" > "Deploy from GitHub repo".
    *   Select your `career-os` repository.
2.  **Configure Environment Variables**:
    Before the build completes, go to the "Variables" tab and add the following:

    | Variable | Description |
    | :--- | :--- |
    | `OPENAI_API_KEY` | Your OpenAI API key (sk-...) |
    | `SUPABASE_URL` | Your Supabase Project URL |
    | `SUPABASE_KEY` | Your Supabase `anon public` key |
    | `SUPABASE_SERVICE_KEY` | Your Supabase `service_role` key |
    | `DATABASE_URL` | Connection string from Supabase (under Database settings) |
    | `SECRET_KEY` | A long random string for security |
    | `REDIS_URL` | Connection string for Redis (see step 3) |

3.  **Add Redis**:
    *   In your Railway project, click "New" > "Database" > "Redis".
    *   Once created, copy the `REDIS_URL` and add it to your Backend service variables.
4.  **Deploy**:
    *   Railway will automatically build and deploy using the `railway.json` settings.
    *   **Verify**: Once deployed, you will get a public URL (e.g., `https://web-production-xxxx.up.railway.app`). Open `https://<YOUR_URL>/docs` to see the API documentation.

## 3. Worker Setup (Railway)

For background tasks (Celery agents), you need to run a worker process.

1.  **Add Service**:
    *   In the same Railway project, add the GitHub repo again (or use "Monorepo" setup if you know how).
    *   Alternatively, you can define multiple services in `railway.toml` (recommended for advanced users) or just run the worker in the main container (not recommended for high scale).
    *   **Recommended**: Create a *Shell* service or a second instance of the repo.
2.  **Start Command**:
    *   Override the "Start Command" in settings to: `cd backend && celery -A tasks.celery_app worker --loglevel=info --pool=solo`
3.  **Variables**: Use the exact same variables as the Backend service.

## 4. Frontend Deployment (Vercel)

1.  **Import Project**:
    *   Log in to Vercel.
    *   Click "Add New..." > "Project".
    *   Import your `career-os` repository.
2.  **Configure Build**:
    *   **Framework Preset**: Next.js
    *   **Root Directory**: `frontend` (Important: Click "Edit" and select the `frontend` folder).
3.  **Environment Variables**:
    Add the following environment variables:

    | Variable | Description |
    | :--- | :--- |
    | `NEXT_PUBLIC_API_URL` | The Railway Backend URL (no trailing slash) |
    | `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase Project URL |
    | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase `anon public` key |

4.  **Deploy**:
    *   Click "Deploy".
    *   Vercel will build and serve the application.
    *   **Verify**: Open the provided Vercel URL. You should see the dashboard.

## 5. Verification Checklist

1.  **Frontend Load**: The dashboard loads without errors.
2.  **Login/Auth**: (If enabled) You can sign up/login.
3.  **API Connectivity**: Check the browser network tab to ensure calls to `/api/...` are succeeding (200 OK).
4.  **Database Connection**: Create a test contact or task to verify data persistence in Supabase.
5.  **Agent Execution**: Trigger a "Discovery" task and check Railway logs to see the agents in action.

## Troubleshooting

*   **CORS Errors**: If you see CORS errors in the browser console, ensure your Backend `api/main.py` has the Vercel domain added to the `allow_origins` list (or `["*"]` for testing).
*   **Build Failures**: Check that you pointed Vercel to the `frontend` directory, not the root.
*   **Database Errors**: Ensure you ran the `setup_db.sql` script.
