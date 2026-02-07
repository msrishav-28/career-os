# CareerOS API Documentation

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![OpenAPI](https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapi-initiative&logoColor=white)

Complete API reference for the CareerOS backend.

## Connection Details

*   **Development URL**: `http://localhost:8000`
*   **Production URL**: `https://your-app.railway.app`
*   **Interactive Docs**: `/docs` (Swagger UI)
*   **Alternative Docs**: `/redoc` (ReDoc)

## Authentication

Currently uses a simple `user_id` query parameter for demonstration. Production deployments should implement JWT authentication via the Authorization header.

## Resources

### Profile

**Store Profile**
`POST /api/profile/store?user_id={user_id}`

Stores user resume data, skills, and goals.
*   **Body**: JSON object containing `skills`, `projects`, `experiences`, `goals`.
*   **Returns**: 200 OK with confirmation.

**Query Profile**
`GET /api/profile/query?user_id={user_id}&query={query}`

Semantic search against the user's profile using vector embeddings.

### Contacts (CRM)

**Create Contact**
`POST /api/contacts/?user_id={user_id}`

Adds a new person to the CRM.
*   **Body**: `name`, `email`, `linkedin_url`, `company`, `contact_type`.

**List Contacts**
`GET /api/contacts/?user_id={user_id}&status={status}&limit={limit}`

Retrieves contacts with optional filtering.

**Pipeline Summary**
`GET /api/contacts/pipeline/summary?user_id={user_id}`

Returns counts of contacts at each stage (discovered, contacted, responded).

### Messages (Outreach)

**Generate Message**
`POST /api/messages/generate`

Uses LLMs to generate a personalized outreach message.
*   **Params**: `user_id`, `contact_id`, `context` (e.g., "internship application").
*   **Returns**: A list of message drafts with personalization scores.

**Create Message**
`POST /api/messages/`

Saves a message draft or sent message.

**Approve Message**
`POST /api/messages/{message_id}/approve`

Marks a draft as approved for sending by the background worker.

### Opportunities

**Discover**
`POST /api/opportunities/discover`

Triggers the AI Discovery Agent to scrape and find new opportunities.
*   **Params**: `keywords`, `location`.

**List Opportunities**
`GET /api/opportunities/`

Lists found jobs or internships, sorted by match score.

### Campaigns

**Create Campaign**
`POST /api/campaigns/`

Starts a new outreach campaign.
*   **Body**: `name`, `type` (career/research), `target_persona`.

**Get Metrics**
`GET /api/campaigns/{id}/metrics`

Returns aggregate stats: total sent, response rate, average score.

### Analytics

**Dashboard Summary**
`GET /api/analytics/dashboard`

Aggregate view of all system metrics for the frontend dashboard.

**Network Health**
`GET /api/analytics/network-health`

Analysis of the user's professional network growth and quality.

## Error Handling

The API uses standard HTTP status codes:
*   `200`: Success
*   `400`: Bad Request (Invalid parameters)
*   `404`: Resource Not Found
*   `429`: Too Many Requests (Rate limit exceeded)
*   `500`: Internal Server Error

## Rate Limiting

Standard limits (configurable):
*   **LinkedIn**: 15 connections/day
*   **Emails**: 50/day

Response headers include `X-RateLimit-Remaining`.

## SDK

Example Python usage:

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "demo-user"

# Create a contact
response = requests.post(
    f"{BASE_URL}/api/contacts/?user_id={USER_ID}",
    json={
        "name": "Jane Doe",
        "company": "Tech Corp",
        "title": "CTO"
    }
)
print(response.json())
```
