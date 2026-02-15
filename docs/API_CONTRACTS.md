# CareerOS: API Contracts & Endpoints

**Version:** 1.0  
**Last Updated:** February 15, 2026  
**Owner:** Backend Team

---

## Base URL

**Production:** `https://api.careeros.com`  
**Staging:** `https://api-staging.careeros.com`

All API requests must include an `Authorization` header with a valid bearer token.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Message Approval Flow](#message-approval-flow)
3. [Onboarding Flow](#onboarding-flow)
4. [System Control](#system-control)
5. [Analytics](#analytics)
6. [Error Codes](#error-codes)
7. [Rate Limits](#rate-limits)
8. [Webhooks](#webhooks)

---

## 1. Authentication

### POST /auth/login

Authenticate user and receive access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_abc123",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "session": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "refresh_xyz789",
      "expires_at": "2026-02-16T21:30:00Z"
    }
  }
}
```

### POST /auth/refresh

Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "refresh_xyz789"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2026-02-16T22:30:00Z"
  }
}
```

---

## 2. Message Approval Flow

### GET /messages/pending

Retrieve pending message drafts for approval.

**Query Parameters:**
- `limit` (optional): Number of drafts to return (default: 5, max: 20)
- `offset` (optional): Pagination offset

**Response (200):**
```json
{
  "success": true,
  "data": {
    "drafts": [
      {
        "id": "msg_001",
        "contact": {
          "id": "contact_123",
          "name": "Jane Smith",
          "title": "ML Engineer",
          "company": "OpenAI",
          "linkedin_url": "https://linkedin.com/in/janesmith"
        },
        "message": {
          "subject": "Your CVPR 2024 paper on vision transformers",
          "body": "Hi Jane,\\n\\nI recently read your CVPR 2024 paper...",
          "preview": "Hi Jane, I recently read your CVPR 2024 paper..."
        },
        "quality_score": 87,
        "personalization_score": 92,
        "generated_at": "2026-02-15T20:30:00Z"
      }
    ],
    "total": 15,
    "has_more": true
  }
}
```

### POST /messages/{message_id}/approve

Approve a message draft for sending.

**Request:**
```json
{
  "schedule": "immediate",
  "edits": {
    "subject": "Optional edited subject",
    "body": "Optional edited body"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": {
      "id": "msg_001",
      "status": "approved",
      "scheduled_at": "2026-02-15T21:00:00Z"
    }
  }
}
```

### POST /messages/{message_id}/reject

Reject a message draft.

**Request:**
```json
{
  "reason": "too_generic",
  "feedback": "Needs more specific personalization"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message_id": "msg_001",
    "status": "rejected"
  }
}
```

### POST /messages/{message_id}/regenerate

Request regeneration of a message draft.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "new_message_id": "msg_002",
    "status": "generating"
  }
}
```

### POST /messages/bulk-approve

Approve multiple messages at once.

**Request:**
```json
{
  "message_ids": ["msg_001", "msg_002", "msg_003"],
  "schedule": "immediate"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "approved": 3,
    "failed": 0
  }
}
```

---

## 3. Onboarding Flow

### POST /onboarding/resume

Upload resume for parsing.

**Request:**
Multipart form data with file upload.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "upload_id": "upload_abc123",
    "status": "processing"
  }
}
```

### GET /onboarding/resume/{upload_id}/status

Check resume parsing status.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "complete",
    "extracted_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "skills": ["Python", "Machine Learning", "PyTorch"],
      "experience": [
        {
          "title": "ML Engineer",
          "company": "TechCorp",
          "duration": "2 years"
        }
      ],
      "education": [
        {
          "degree": "B.S. Computer Science",
          "university": "Stanford",
          "year": 2022
        }
      ]
    }
  }
}
```

### POST /onboarding/objectives

Set user objectives and preferences.

**Request:**
```json
{
  "target_roles": ["ML Engineer", "Research Scientist"],
  "target_companies": ["OpenAI", "DeepMind"],
  "locations": ["Remote", "San Francisco"],
  "exclusions": {
    "companies": ["Acme Corp"],
    "keywords": ["sales"]
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "objectives_saved": true
  }
}
```

### POST /onboarding/simulate

Run simulation to estimate matches.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "estimated_matches": 150,
    "sample_contacts": [
      {
        "name": "Alice Johnson",
        "title": "Hiring Manager",
        "company": "OpenAI"
      }
    ],
    "confidence": "high"
  }
}
```

---

## 4. System Control

### POST /system/pause

Pause all message generation and sending.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "system_status": "paused",
    "paused_at": "2026-02-15T21:30:00Z"
  }
}
```

### POST /system/resume

Resume message generation and sending.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "system_status": "active",
    "resumed_at": "2026-02-15T21:35:00Z"
  }
}
```

### GET /system/status

Get current system status.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "active",
    "pending_messages": 15,
    "messages_sent_today": 8,
    "daily_limit": 50,
    "health": {
      "database": "healthy",
      "queue": "healthy",
      "ai_service": "healthy"
    }
  }
}
```

---

## 5. Analytics

### GET /analytics/dashboard

Get dashboard analytics.

**Query Parameters:**
- `period` (optional): "week" | "month" | "all_time" (default: "week")

**Response (200):**
```json
{
  "success": true,
  "data": {
    "messages_generated": 45,
    "messages_sent": 32,
    "response_rate": 0.22,
    "avg_quality_score": 85,
    "contacts_discovered": 150
  }
}
```

---

## 6. Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | System is paused or under maintenance |

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Email is required",
    "field": "email"
  }
}
```

---

## 7. Rate Limits

**Per User:**
- 100 requests per minute
- 1000 requests per hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1708034400
```

**When Rate Limited (429):**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again in 30 seconds.",
    "retry_after": 30
  }
}
```

---

## 8. Webhooks

### Webhook Events

**message.approved:**
```json
{
  "event": "message.approved",
  "timestamp": "2026-02-15T21:30:00Z",
  "data": {
    "message_id": "msg_001",
    "contact_id": "contact_123"
  }
}
```

**message.sent:**
```json
{
  "event": "message.sent",
  "timestamp": "2026-02-15T21:31:00Z",
  "data": {
    "message_id": "msg_001",
    "sent_at": "2026-02-15T21:31:00Z"
  }
}
```

**message.response_received:**
```json
{
  "event": "message.response_received",
  "timestamp": "2026-02-16T10:00:00Z",
  "data": {
    "message_id": "msg_001",
    "response_preview": "Thanks for reaching out..."
  }
}
```

---

**Document Owner:** Backend Team  
**Last Updated:** February 15, 2026