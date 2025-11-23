# CareerOS API Documentation

Complete API reference for CareerOS backend.

**Base URL:** `http://localhost:8000` (development)  
**Production URL:** `https://your-app.railway.app`

**API Documentation:** `/docs` (Swagger UI)  
**Alternative Docs:** `/redoc` (ReDoc)

---

## Authentication

Currently using simple user_id parameter. Production should implement proper JWT authentication.

---

## Profile API

### Store Profile
```http
POST /api/profile/store?user_id={user_id}
Content-Type: application/json

{
  "skills": ["Python", "Machine Learning"],
  "projects": [{
    "name": "AI Chatbot",
    "description": "Built using GPT-4",
    "tech_stack": "Python, OpenAI, FastAPI",
    "url": "https://github.com/..."
  }],
  "experiences": [],
  "education": [],
  "goals": [{
    "goal": "Land AI/ML internship",
    "priority": "high",
    "deadline": "2026-03-01"
  }],
  "interests": ["AI", "Startups"],
  "achievements": []
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile stored successfully",
  "user_id": "demo-user"
}
```

### Query Profile
```http
GET /api/profile/query?user_id={user_id}&query={query}&n_results=5
```

**Response:** `200 OK`
```json
{
  "results": [...],
  "count": 5
}
```

---

## Contacts API

### Create Contact
```http
POST /api/contacts/?user_id={user_id}
Content-Type: application/json

{
  "name": "John Smith",
  "email": "john@example.com",
  "linkedin_url": "https://linkedin.com/in/johnsmith",
  "company": "Google",
  "title": "ML Engineer",
  "tags": ["hiring_manager", "ai"],
  "contact_type": "career",
  "quality_score": 8
}
```

### List Contacts
```http
GET /api/contacts/?user_id={user_id}&status=contacted&limit=100
```

### Update Contact
```http
PUT /api/contacts/{contact_id}
Content-Type: application/json

{
  "status": "responded",
  "quality_score": 9
}
```

### Pipeline Summary
```http
GET /api/contacts/pipeline/summary?user_id={user_id}
```

**Response:**
```json
{
  "discovered": 45,
  "to_contact": 12,
  "contacted": 23,
  "responded": 15,
  "converted": 5
}
```

---

## Messages API

### Generate Message
```http
POST /api/messages/generate?user_id={user_id}&contact_id={contact_id}&context=internship%20application
```

**Response:** Message drafts with scores

### Create Message
```http
POST /api/messages/?user_id={user_id}
Content-Type: application/json

{
  "contact_id": "uuid",
  "campaign_id": "uuid",
  "platform": "email",
  "subject": "Question about your ML work",
  "body": "Hi John...",
  "personalization_score": 85
}
```

### Get Approval Queue
```http
GET /api/messages/approval-queue?user_id={user_id}
```

### Approve Message
```http
POST /api/messages/{message_id}/approve
```

---

## Opportunities API

### Discover Opportunities
```http
POST /api/opportunities/discover?user_id={user_id}&keywords=AI%20ML&location=India
```

### List Opportunities
```http
GET /api/opportunities/?user_id={user_id}&min_match_score=7&limit=20
```

### Update Opportunity
```http
PUT /api/opportunities/{opportunity_id}
Content-Type: application/json

{
  "status": "applied",
  "metadata": {"notes": "Applied via referral"}
}
```

---

## Campaigns API

### Create Campaign
```http
POST /api/campaigns/?user_id={user_id}
Content-Type: application/json

{
  "name": "AI/ML Internship Outreach - Nov 2025",
  "campaign_type": "career",
  "target_persona": "ML hiring managers",
  "daily_outreach_limit": 15,
  "min_personalization_score": 75
}
```

### Get Campaign Metrics
```http
GET /api/campaigns/{campaign_id}/metrics?user_id={user_id}
```

**Response:**
```json
{
  "campaign_id": "uuid",
  "total_sent": 50,
  "total_replied": 15,
  "response_rate": 30.0,
  "avg_personalization_score": 82.5
}
```

---

## Analytics API

### Dashboard Summary
```http
GET /api/analytics/dashboard?user_id={user_id}&days=7
```

**Response:**
```json
{
  "period_days": 7,
  "outreach": {
    "messages_sent": 35,
    "response_rate": 28.5,
    "avg_personalization": 78.2
  },
  "pipeline": {
    "total_contacts": 150,
    "conversion_rate": 25.5,
    "by_status": {...}
  },
  "network": {
    "health_score": 8,
    "total_contacts": 150
  },
  "skill_gaps": {
    "gaps_identified": 3,
    "top_gap": {"skill": "React", "frequency": 12}
  }
}
```

### Outreach Analytics
```http
GET /api/analytics/outreach?user_id={user_id}&days=30
```

### Skill Gaps
```http
GET /api/analytics/skill-gaps?user_id={user_id}
```

### Network Health
```http
GET /api/analytics/network-health?user_id={user_id}
```

---

## Tasks API

### Generate Outreach Async
```http
POST /api/tasks/outreach/generate-async?user_id={user_id}&contact_id={id}&context=...
```

**Response:**
```json
{
  "message": "Outreach generation started",
  "task_id": "abc-123",
  "status": "processing"
}
```

### Check Task Status
```http
GET /api/tasks/task/{task_id}
```

### Trigger Scheduled Task
```http
POST /api/tasks/scheduled/trigger/weekly_report
```

### Get Scheduled Tasks Status
```http
GET /api/tasks/scheduled/status
```

---

## Rate Limits

Default limits per user per day:
- LinkedIn connections: 15
- LinkedIn profile views: 80
- Emails: 50

Configurable via user settings.

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## Pagination

Most list endpoints support pagination:

```http
GET /api/contacts/?user_id={user_id}&limit=100&offset=0
```

---

## Filtering

Endpoints support various filters:

```http
# Filter by status
GET /api/contacts/?user_id={user_id}&status=responded

# Filter by type
GET /api/opportunities/?user_id={user_id}&opportunity_type=internship

# Filter by score
GET /api/opportunities/?user_id={user_id}&min_match_score=7
```

---

## Webhooks (Future)

Coming soon: Webhooks for events like:
- Message replied
- Opportunity discovered
- Weekly report generated

---

## SDKs

Python SDK example:

```python
from careeros_client import CareerOSClient

client = CareerOSClient(
    api_url="https://your-app.railway.app",
    user_id="your-user-id"
)

# Create contact
contact = client.contacts.create(
    name="John Smith",
    company="Google",
    title="ML Engineer"
)

# Generate outreach
drafts = client.messages.generate(
    contact_id=contact.id,
    context="internship application"
)
```

---

## Rate Limiting Headers

Responses include rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Best Practices

1. **Always check rate limits** before bulk operations
2. **Use async endpoints** for long-running tasks
3. **Poll task status** for async operations
4. **Implement retries** with exponential backoff
5. **Cache responses** when appropriate
6. **Handle errors gracefully**

---

## Support

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- GitHub: Issues
- Email: support@careeros.dev
