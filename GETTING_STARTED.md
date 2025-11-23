# Getting Started with CareerOS

This guide will help you get CareerOS up and running in under 30 minutes.

## Step 1: Prerequisites

Install the following:
- **Python 3.10+**: Download from [python.org](https://python.org)
- **Node.js 18+**: Download from [nodejs.org](https://nodejs.org)
- **Git**: Download from [git-scm.com](https://git-scm.com)

## Step 2: Get API Keys

### Required APIs

1. **OpenAI API Key**
   - Go to [platform.openai.com](https://platform.openai.com)
   - Create account and add payment method
   - Generate API key
   - Cost: ~$1-5/month for testing

2. **Supabase Account**
   - Go to [supabase.com](https://supabase.com)
   - Create free account
   - Create new project
   - Note URL and anon key

### Optional APIs (for full functionality)

3. **Resend** (for email sending)
   - Go to [resend.com](https://resend.com)
   - 10,000 emails/month free

## Step 3: Setup Backend

```bash
# Clone repository
git clone <your-repo-url>
cd CareerOS/backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env

# Edit .env file with your credentials:
# - OPENAI_API_KEY
# - SUPABASE_URL
# - SUPABASE_KEY
# - DATABASE_URL (from Supabase)
# - SECRET_KEY (generate with: openssl rand -hex 32)
```

## Step 4: Setup Database

1. Open Supabase Dashboard
2. Go to SQL Editor
3. Copy content from `backend/scripts/setup_db.sql`
4. Paste and run in SQL Editor
5. Verify tables created successfully

## Step 5: Start Backend

```bash
cd backend
uvicorn api.main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see API documentation.

## Step 6: Setup Frontend

Open a new terminal:

```bash
cd CareerOS/frontend

# Install dependencies
npm install

# Configure environment
copy .env.local.example .env.local

# Edit .env.local:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY

# Start development server
npm run dev
```

Visit http://localhost:3000

## Step 7: First Use

### 1. Create Your Profile

```bash
# Use API or frontend to store your profile
curl -X POST "http://localhost:8000/api/profile/store?user_id=demo-user" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "Machine Learning", "FastAPI"],
    "projects": [
      {
        "name": "AI Chatbot",
        "description": "Built using GPT-4",
        "tech_stack": "Python, OpenAI, FastAPI"
      }
    ],
    "goals": [
      {
        "goal": "Land AI/ML internship",
        "priority": "high",
        "deadline": "2026-03-01"
      }
    ],
    "experiences": [],
    "education": [],
    "interests": ["AI", "Machine Learning", "Startups"],
    "achievements": []
  }'
```

### 2. Discover Opportunities

```bash
curl -X POST "http://localhost:8000/api/opportunities/discover?user_id=demo-user&keywords=AI%20ML%20internship&location=India"
```

### 3. Generate Outreach Message

First, create a contact:

```bash
curl -X POST "http://localhost:8000/api/contacts/?user_id=demo-user" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "company": "Google",
    "title": "ML Engineer",
    "contact_type": "career",
    "quality_score": 8
  }'
```

Then generate message (use contact_id from response):

```bash
curl -X POST "http://localhost:8000/api/messages/generate?user_id=demo-user&contact_id=<contact-id>&context=internship%20application"
```

## Troubleshooting

### Backend Issues

**Error: "Cannot connect to database"**
- Check SUPABASE_URL and DATABASE_URL in .env
- Verify database tables created correctly

**Error: "OpenAI API key invalid"**
- Check OPENAI_API_KEY in .env
- Ensure you have credits in OpenAI account

### Frontend Issues

**Error: "Cannot connect to API"**
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in .env.local

**Build errors**
- Delete node_modules and package-lock.json
- Run `npm install` again

### Redis Issues

**Error: "Cannot connect to Redis"**
- Install Redis locally or use Redis Cloud free tier
- Update REDIS_URL in .env

## Next Steps

1. **Customize Agents**: Edit prompts in `backend/config/prompts.py`
2. **Add More Tools**: Create new tools in `backend/tools/`
3. **Build UI**: Customize frontend components
4. **Deploy**: Follow deployment guide for production

## Getting Help

- 📖 Read full documentation in `/docs`
- 🐛 Report issues on GitHub
- 💬 Join Discord community
- 📧 Email: support@careeros.dev

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Database tables created
- [ ] Profile stored successfully
- [ ] Can discover opportunities
- [ ] Can generate messages

Congratulations! You're ready to use CareerOS! 🎉
