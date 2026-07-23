# AI-XP - AI Customer Experience Platform

Enterprise-grade AI Customer Experience platform. Open-source alternative to HubSpot, Freshdesk, Zendesk, Intercom, and Salesforce Service Cloud.

## Features

- **Multi-tenant SaaS CRM**
- **AI Chat & Assistant** (Ollama + OpenAI fallback)
- **Knowledge Base with RAG**
- **Multi-channel Communication** (WhatsApp, Telegram, Email, Messenger, Webhook, WordPress)
- **Campaign Management**
- **Automation Workflows**
- **Deal & Lead Pipeline**
- **Task & Note Management**
- **File Storage** (MinIO)
- **JWT Authentication & RBAC**
- **Audit Logs**

## Quick Start

```bash
# Clone repository
git clone https://github.com/nwarict/aixp.git
cd aixp

# Run bootstrap
chmod +x bootstrap.sh
./bootstrap.sh
```

## Default Login

- **Email**: admin@aixp.local
- **Password**: admin123

**Change immediately after first login!**

## Architecture

- **Backend**: FastAPI, SQLAlchemy Async, PostgreSQL + pgvector, Redis, Celery
- **Frontend**: Vue 3, Vuetify, Vite
- **AI**: Ollama (local LLM) + OpenAI fallback
- **Storage**: MinIO
- **Infrastructure**: Docker Compose, Nginx

## API Documentation

- Swagger UI: http://localhost/api/docs
- ReDoc: http://localhost/api/redoc

## License

MIT
