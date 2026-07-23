# Changelog

## [1.0.0] - 2024

### Added
- Complete multi-tenant SaaS architecture
- FastAPI backend with async SQLAlchemy
- Vue 3 + Vuetify frontend
- AI Chat with Ollama and OpenAI fallback
- Knowledge Base with pgvector embeddings
- WhatsApp, Telegram, Email, Messenger connectors
- Campaign management system
- Automation workflows
- Deal and lead pipeline
- Task and note management
- JWT authentication with RBAC
- Audit logging
- Docker Compose deployment
- Nginx reverse proxy
- MinIO file storage
- Celery background jobs
- Alembic database migrations

### Security
- Secure password hashing with bcrypt
- JWT access and refresh tokens
- Role-based access control
- Rate limiting middleware
- Tenant isolation

### Infrastructure
- Health checks for all services
- Proper service dependencies
- Environment-based configuration
- Bootstrap script for Ubuntu VPS
