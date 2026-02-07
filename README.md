# CareerOS

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

CareerOS is an AI-powered platform designed to accelerate career growth and networking through automation. It leverages a multi-agent system to discover opportunities, manage professional relationships, and automate outreach, allowing users to focus on high-value interactions.

## Key Features

*   **Multi-Agent Architecture**: Orchestrates six specialized AI agents for discovery, outreach, research, and profile management.
*   **Intelligent Discovery**: Automates the search for job opportunities, GitHub repositories, and research papers (via arXiv and Google Scholar).
*   **Personalized Outreach**: Generates context-aware, high-quality messages for LinkedIn and email using LLMs.
*   **Research Module**: Specialized capabilities for academic discovery, including faculty scraping and publication matching.
*   **CRM & Analytics**: comprehensive dashboard for tracking contacts, campaigns, and engagement metrics.
*   **Production Ready**: Fully dockerized with CI/CD pipelines and scalable infrastructure.

## Architecture Overview

The system is split into two core components:

### Backend
*   **Framework**: FastAPI (Python)
*   **AI Engine**: CrewAI + LangChain + OpenAI GPT-4
*   **Database**: Supabase (PostgreSQL) + ChromaDB (Vector Store)
*   **Task Queue**: Celery + Redis

### Frontend
*   **Framework**: Next.js 14 (App Router)
*   **Styling**: Tailwind CSS + Shadcn UI
*   **State Management**: Zustand

## Quick Start

### Prerequisites
*   Docker and Docker Compose
*   OpenAI API Key
*   Supabase Account

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/msrishav-28/career-os.git
    cd career-os
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory (see `env.example` for reference).

3.  **Start Services**
    ```bash
    docker-compose up -d
    ```

The application will be available at:
*   **Frontend**: http://localhost:3000
*   **Backend API**: http://localhost:8000
*   **API Documentation**: http://localhost:8000/docs

## Documentation

*   [Getting Started](GETTING_STARTED.md): Detailed setup and usage guide.
*   [Deployment Guide](docs/DEPLOYMENT.md): Instructions for deploying to Railway and Vercel.
*   [API Reference](docs/API.md): Endpoint documentation.
*   [Contributing](docs/CONTRIBUTING.md): Guidelines for code contributions.
*   [Research Module](docs/RESEARCH_MODULE.md): Documentation for the academic discovery features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
