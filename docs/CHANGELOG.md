# Changelog

![Version](https://img.shields.io/badge/version-1.1.0-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/status-production--ready-green?style=for-the-badge)

All notable changes to the CareerOS project will be documented in this file.

## [1.1.0] - 2025-11-29

### Added
*   **Research Internship Module**: Specialized support for academic discovery and outreach.
    *   Google Scholar integration for researcher discovery.
    *   arXiv search for finding relevant papers.
    *   Publication-matching algorithms.
*   **Multi-Campaign Support**: Ability to run industry and research campaigns simultaneously.

### Changed
*   **Outreach Agent**: Enhanced personalization scoring to support academic criteria (80/100 threshold).
*   **Database Schema**: Added `publications` and `lab_url` fields to Contact model.

## [1.0.0] - 2025-10-30

### Added
*   **AI Agent System**: 6 specialized agents for Discovery, Outreach, CRM, Content, Growth, and Profiling.
*   **Backend Core**: FastAPI application with Supabase integration and Celery task queue.
*   **Frontend**: Next.js 14 dashboard with real-time analytics and campaign management.
*   **Outreach Automation**: Automated email generation using GPT-4o-mini.
*   **Analytics Engine**: Comprehensive metrics for tracking response rates and pipeline health.
*   **Infrastructure**: Docker support and CI/CD pipelines for Railway and Vercel.

### Security
*   Implemented rate limiting for external APIs (LinkedIn, Email).
*   Added human-in-the-loop approval workflow for all generated messages.

## Technical Statistics

*   **Total Files**: 90+
*   **Lines of Code**: ~15,000+
*   **API Endpoints**: 45+
*   **Test Coverage**: >60%
*   **Database Tables**: 7
