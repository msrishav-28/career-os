# CareerOS: Future SaaS & Multi-Tenant Architecture

**Version:** 1.0
**Last Updated:** February 15, 2026
**Owner:** Product & Engineering Team

---

## Vision: Beyond Single-User Product

### Current State (v1.0)

**CareerOS Today:**
- Single-user SaaS ($10K/year)
- Each user has isolated account
- LinkedIn automation for job seekers
- Manual approval workflow

**Limitations:**
- No team collaboration
- No reseller opportunities
- No enterprise sales potential

### Future State (v2.0+)

**CareerOS as Multi-Tenant Platform:**
1. **Career Services** - Universities offering alumni support
2. **Recruiting Agencies** - Outbound sourcing for clients
3. **Enterprise HR** - Internal talent acquisition
4. **Coaching Businesses** - Career coaches serving clients
5. **White-Label Partners** - Reselling under their brand

**Example:**

**Stanford Career Center**
- 50 seat licenses for counselors
- 10,000 alumni accounts
- Stanford-branded interface
- Usage: 5,000 messages/month
- Cost: $50K/year

---

## Multi-Tenant Architecture

### Tenancy Models

**Option 1: Shared Database (Recommended for v2.0)**

**Pros:**
- Simplest to implement
- Cost-effective
- Easy cross-tenant analytics

**Cons:**
- Must ensure query filters include tenant_id
- One bad query affects all tenants

**Schema:**
All tables include tenant_id column with foreign key to tenants table.

---

**Option 2: Separate Database (For Enterprise)**

**Pros:**
- Complete isolation
- Easy backup/restore per tenant
- Tenant-specific schema changes

**Cons:**
- Higher operational complexity
- More expensive
- Cross-tenant analytics harder

**When to Use:**
- Enterprise clients requiring data residency
- White-label partners needing full control
- Tenants with >100K records

---

**Option 3: Schema-Based (Middle Ground)**

**Pros:**
- Logical isolation within one database
- Better than row-level, simpler than separate DBs

**Cons:**
- More complex than Option 1
- Still shares database resources

### Recommended Approach

**Phase 1 (v2.0):** Shared database with tenant_id
**Phase 2 (v3.0):** Schema-based for mid-tier
**Phase 3 (Enterprise):** Separate database for large clients

---

## Pricing Tier Strategy

### Proposed Tiers

| Tier | Price | Seats | Messages/Month |
|------|-------|-------|----------------|
| **Individual** | $10K/year | 1 | 500 |
| **Team** | $25K/year | 5 | 2,000 |
| **Business** | $60K/year | 20 | 10,000 |
| **Enterprise** | Custom | Unlimited | Unlimited |

### Feature Matrix

| Feature | Individual | Team | Business | Enterprise |
|---------|-----------|------|----------|------------|
| Message Generation | ✅ | ✅ | ✅ | ✅ |
| Multiple Users | ❌ | ✅ | ✅ | ✅ |
| Shared Contacts | ❌ | ✅ | ✅ | ✅ |
| Custom Branding | ❌ | ❌ | ✅ | ✅ |
| White-Label Domain | ❌ | ❌ | ✅ | ✅ |
| API Access | ❌ | ❌ | ✅ | ✅ |
| SSO (SAML) | ❌ | ❌ | ❌ | ✅ |
| Dedicated Support | ❌ | ❌ | ❌ | ✅ |

### Usage-Based Add-Ons

- Additional messages: $0.50/message
- Additional seats: $2K/year/seat
- Priority support: $5K/year

---

## Tenant Isolation & Security

### Data Isolation

**Critical: Every Query Must Include Tenant Filter**

Extract tenant_id from JWT and add to request context. Use ORM middleware to automatically add tenant_id filter to all queries.

**Test:**
Ensure one tenant cannot access another tenant's data under any circumstances.

### Resource Limits

Define per pricing tier:
- Max contacts
- Max messages per month
- Max campaigns
- Max API calls per hour

---

## Admin Panel Requirements

### Super Admin Dashboard

**Features:**
- View all tenants
- Create/edit/delete tenants
- View tenant usage
- Impersonate tenant for support
- Toggle feature flags per tenant
- System health metrics

### Tenant Admin Dashboard

**Features:**
- Manage users (invite, remove, roles)
- View team usage
- Billing & subscription management
- Customize branding
- Export data (GDPR)

### Role-Based Access Control

**Roles:**
- **Super Admin** - Full system access
- **Tenant Admin** - Manage tenant settings
- **Member** - Use the product
- **Viewer** - Read-only access

---

## Billing & Subscription Management

### Stripe Integration

Use Stripe Subscriptions API for recurring billing. Support multiple line items (base plan + seats + usage).

### Usage-Based Billing

Track message generation and API calls. Use Stripe metered billing for overages.

### Self-Service Portal

Integrate Stripe Customer Portal for tenants to manage subscriptions and view invoices.

---

## White-Label / Theming

### Custom Branding

**Settings:**
- Logo URL
- Primary color
- Secondary color
- Custom domain (optional)
- Custom email domain (optional)

**Implementation:**
Load tenant branding on app init and apply CSS custom properties dynamically.

### Custom Domains

**Setup:**
1. Tenant provides domain (e.g., recruit.techrecruit.com)
2. Tenant adds CNAME: recruit.techrecruit.com → cname.careeros.com
3. Verify DNS, provision SSL cert
4. Route based on Host header

---

## Usage Analytics Per Tenant

### Tenant Dashboard Metrics

- Messages generated (this month)
- Messages approved
- Response rate
- Average quality score
- Active users
- API calls

### Super Admin Analytics

- Total revenue (MRR)
- Churn rate
- Most active tenants
- Tenants approaching limits
- Feature usage by tier

---

## Enterprise Features

### Single Sign-On (SSO)

**SAML 2.0:**
Enterprise clients use their identity provider (Okta, Azure AD). CareerOS acts as Service Provider.

### API Access

Provide comprehensive REST API for enterprise customers to integrate CareerOS into existing systems.

---

## Migration Path

### Phase 1: Prepare Data Model

Add tenant_id column to all tables. Create default tenant for existing users.

### Phase 2: Add Tenant Context

Update all queries to include tenant_id filter. Add middleware to extract tenant context.

### Phase 3: Build Admin Panel

Create super admin dashboard and tenant management.

### Phase 4: Launch Team Plan

Update marketing, add new pricing tiers, enable self-service signup.

---

## When to Start

**Triggers:**
- After reaching $100K ARR with individuals
- When you have 3+ enterprise inquiries
- When you have 2-3 months engineering bandwidth

**Priority Order:**
1. Basic multi-user support (Team plan)
2. Billing & subscription management
3. White-label / custom branding
4. SSO and enterprise features
5. API access

---

**Document Owner:** Product Team
**Review Cycle:** Quarterly
**Last Updated:** February 15, 2026