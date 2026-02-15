# CareerOS: Content & Tone Guidelines for Generated Messages

**Version:** 1.0
**Last Updated:** February 15, 2026
**Owner:** Product & AI Team

---

## Core Philosophy

**Cold outreach is not spam when it's genuinely personalized, respectful, and relevant.**

### The 3 Pillars

1. **Relevance** - Every message must demonstrate why THIS person matters to THIS user
2. **Respect** - Acknowledge the recipient's time and expertise  
3. **Value Exchange** - What can the user offer and what are they seeking

---

## Brand Voice

**Key Principle:** CareerOS adapts to the user's voice, not the other way around.

### Voice Attributes

- **Professional** - Respectful but not stiff
- **Curious** - Genuine interest, not flattery
- **Humble** - Aware of power dynamics
- **Specific** - Concrete details, not vague praise
- **Concise** - Respects recipient's time (150-250 words industry, 200-300 academic)

---

## Message Templates

### Industry Outreach

**Structure:**
1. Hook (1 sentence) - Specific reference to their work
2. Context (2-3 sentences) - Who you are, your background
3. Connection (1-2 sentences) - Why you're reaching out
4. Ask (1 sentence) - Clear, low-commitment request
5. Sign-off (1 sentence) - Gracious close

**Example:**
```
Subject: Your work on real-time fraud detection at Stripe

Hi Maria,

I saw your talk at PyData 2025 on real-time fraud detection and was blown
away by how you reduced false positives by 40% using ensemble methods.

I'm a recent grad from UC Berkeley (CS + Stats) and just wrapped up a 
capstone project on anomaly detection in financial transactions. We achieved
95% precision using a hybrid LSTM + XGBoost approach.

Would you have 20 minutes for a virtual coffee in the next couple weeks?
I'm exploring roles in ML/fraud detection and would appreciate your insights.

Thanks!
Alex Chen
```

### Academic Outreach

**Structure:**
1. Research Hook (1-2 sentences) - Specific paper or research
2. Credentials (2-3 sentences) - Your academic background
3. Alignment (2-3 sentences) - How interests align
4. Ask (1-2 sentences) - PhD/postdoc/collaboration
5. Attachment Note - Reference CV/papers

---

## Personalization Requirements

### Minimum Bar

Every message MUST include at least **3 personalization tokens**:

- Recent Work (paper, blog, talk, GitHub project)
- Company News (product launch, funding)
- Shared Interest (technology, research area)
- Mutual Connection
- Geographic (location overlap)
- Temporal ("just joined", "recent promotion")
- Educational ("fellow alum")
- Publication (specific paper with detail)

### Personalization Depth Levels

**Level 1 (Insufficient):** "I'm impressed by your work at Google."

**Level 3 (Good):** "I read your blog post on scaling Knowledge Graph embeddings to 100M entities."

**Level 4 (Excellent):** "I read your blog post on scaling Knowledge Graph embeddings, particularly the section on handling long-tail entities using clustering. We faced a similar challenge..."

---

## Quality Scoring Rubric

### Score Formula (0-100)

```
Quality Score = (0.4 × Personalization) + (0.3 × Relevance) + (0.2 × Clarity) + (0.1 × Tone)
```

**Personalization (40%):** Number and depth of specific references
**Relevance (30%):** Alignment with recipient's interests/role  
**Clarity (20%):** Clear purpose, concise, easy to respond
**Tone (10%):** Appropriate formality, natural language

### Approval Thresholds

| Score | Action |
|-------|--------|
| < 60 | Auto-reject |
| 60-69 | Show with warning |
| 70-79 | Show normally (industry default) |
| 80+ | Show normally (academic default) |
| 90+ | "High quality" badge |

---

## Hard Constraints

### Never Include

1. **False Claims** - "I've been following your work for years" (when just found them)
2. **Manipulative Language** - "This is a limited-time opportunity"
3. **Pressure Tactics** - "I need to hear back by Friday"
4. **Generic Flattery** - "You're an inspiration" (without specifics)
5. **Spam Triggers** - ALL CAPS, excessive exclamation marks!!!, "Urgent"

### Length Limits

| Message Type | Min | Max | Optimal |
|--------------|-----|-----|------|
| Industry Cold | 100 | 300 | 200 |
| Academic Cold | 150 | 400 | 280 |
| Follow-Up | 50 | 150 | 100 |

---

## Industry vs Academic Tone

| Dimension | Industry | Academic |
|-----------|----------|----------|
| **Formality** | Professional but casual | Formal, respectful |
| **Length** | 150-250 words | 200-350 words |
| **Focus** | Skills, impact, fit | Research, publications |
| **Opening** | Company news/project | Specific paper |
| **Credentials** | Work experience | Degrees, publications |
| **Ask** | Coffee chat | PhD position, collaboration |

---

## Quality Assurance Checklist

Before showing draft to user:

- [ ] Recipient's name correct and spelled properly
- [ ] At least 3 specific personalizations present
- [ ] Subject line is specific and compelling
- [ ] Length within bounds (100-400 words)
- [ ] Clear single ask (not multiple requests)
- [ ] No prohibited language or spam triggers
- [ ] Appropriate tone for context
- [ ] Quality score ≥ 70 (industry) or ≥ 80 (academic)
- [ ] No grammatical errors
- [ ] Sign-off includes user's name and contact

---

## Examples: Good vs Bad

### Bad Example (Score: 45/100)

```
Subject: Job Opportunity

Hi,

I saw that you work at Google and I'm very interested in working there.
I'm a hardworking student with strong Python and ML skills.

Would you be available to chat about opportunities at Google?

Looking forward to hearing from you!
John
```

**Why it fails:**
- Generic subject
- No personalization
- Focuses on sender, not recipient
- No unique value proposition

### Good Example (Score: 87/100)

```
Subject: Your work on Gemini's multimodal reasoning

Hi Sarah,

I read your Medium post on how Gemini handles cross-modal attention between
text and images. The insight about using separate encoders but shared decoder
layers was fascinating - it's a clever way to preserve modality-specific features.

I'm a CS senior at Berkeley working on my thesis on vision-language models.
I recently built a smaller-scale VLM that achieved 84% accuracy on VQA v2
using a similar architecture.

Would you have 20 minutes for a call to discuss your approach? I'm exploring
full-time roles in multimodal ML and would love to hear about the Gemini team.

Thanks!
John Chen
johnchen.ai | github.com/johnchen
```

**Why it works:**
- Specific subject referencing real work
- Opens with concrete technical detail  
- Shows genuine understanding
- Relevant credentials and achievement
- Clear, respectful ask with time commitment
- Professional signature with links

---

**Document Owner:** AI Product Team
**Review Cycle:** Monthly
**Last Updated:** February 15, 2026