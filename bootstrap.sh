#!/bin/bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "========================================"
echo "  AI-XP Platform - Bootstrap"
echo "  AI Customer Experience SaaS"
echo "========================================"

# Check if running as root for Docker install
NEED_SUDO=""
if [ "$EUID" -ne 0 ]; then
    NEED_SUDO="sudo"
fi

# Step 1: Install Docker if missing
log_info "Checking Docker..."
if ! command -v docker &> /dev/null; then
    log_warn "Docker not found. Installing..."
    $NEED_SUDO apt-get update
    $NEED_SUDO apt-get install -y ca-certificates curl gnupg
    $NEED_SUDO install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $NEED_SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    $NEED_SUDO chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | $NEED_SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null
    $NEED_SUDO apt-get update
    $NEED_SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    $NEED_SUDO usermod -aG docker $USER 2>/dev/null || true
    log_ok "Docker installed"
else
    log_ok "Docker already installed"
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_warn "Docker Compose not found. Installing..."
    $NEED_SUDO apt-get install -y docker-compose-plugin
fi

# Determine docker compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi
log_info "Using: $COMPOSE_CMD"

# Step 2: Create project directory
PROJECT_DIR="$(pwd)/aixp"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
log_ok "Project directory: $PROJECT_DIR"

# Step 3: Generate secrets
log_info "Generating secrets..."
DB_PASSWORD=$(openssl rand -base64 32 2>/dev/null || tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32)
REDIS_PASSWORD=$(openssl rand -base64 32 2>/dev/null || tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32)
MINIO_PASSWORD=$(openssl rand -base64 32 2>/dev/null || tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32)
SECRET_KEY=$(openssl rand -base64 48 2>/dev/null || tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 48)
WP_SECRET=$(openssl rand -base64 24 2>/dev/null || tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 24)

# Step 4: Create .env
cat > .env <<EOF
# Database
DB_USER=aixp
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=aixp
DATABASE_URL=postgresql+asyncpg://aixp:${DB_PASSWORD}@postgres:5432/aixp

# Redis
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Celery
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/2

# MinIO
MINIO_USER=aixpadmin
MINIO_PASSWORD=${MINIO_PASSWORD}
MINIO_BUCKET=aixp-files
MINIO_ENDPOINT=minio:9000

# AI
OLLAMA_HOST=http://ollama:11434
DEFAULT_AI_MODEL=llama3.1:8b
FALLBACK_AI_PROVIDER=
OPENAI_API_KEY=

# Security
SECRET_KEY=${SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
ENVIRONMENT=production
APP_NAME=AI-XP
APP_URL=https://localhost

# Connectors
WHATSAPP_API_KEY=
TELEGRAM_BOT_TOKEN=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

# Meta / Facebook Messenger
META_APP_ID=
META_APP_SECRET=
META_VERIFY_TOKEN=
META_PAGE_ACCESS_TOKEN=

# WordPress
WP_WEBHOOK_SECRET=${WP_SECRET}
EOF

cp .env .env.example
log_ok ".env created with secure secrets"

# Step 5: Create data directories
mkdir -p data/{postgres,redis,minio}
log_ok "Data directories created"

# Step 6: Build and start services
log_info "Building Docker images..."
$COMPOSE_CMD build

log_info "Starting core services..."
$COMPOSE_CMD up -d postgres redis minio

log_info "Waiting for database to be ready..."
sleep 15

# Check if postgres is ready
until $COMPOSE_CMD exec -T postgres pg_isready -U aixp -d aixp 2>/dev/null; do
    log_warn "Database not ready yet, waiting..."
    sleep 5
done
log_ok "Database is ready"

# Step 7: Run migrations and init
log_info "Running database migrations..."
$COMPOSE_CMD exec backend alembic upgrade head 2>/dev/null || true

log_info "Initializing database..."
$COMPOSE_CMD exec backend python -c "from app.core.db import init_db; import asyncio; asyncio.run(init_db())" 2>/dev/null || true

# Step 8: Start all services
log_info "Starting all services..."
$COMPOSE_CMD up -d

# Step 9: Health checks
log_info "Running health checks..."
sleep 10

HEALTH_URL="http://localhost:8000/health"
for i in {1..30}; do
    if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
        log_ok "Backend is healthy"
        break
    fi
    sleep 2
done

# Step 10: Display final info
echo ""
echo "========================================"
echo "  AI-XP Platform Deployed!"
echo "========================================"
echo ""
echo "Services:"
echo "  Frontend:     http://localhost"
echo "  Backend API:  http://localhost/api"
echo "  API Docs:     http://localhost/api/docs"
echo "  MinIO Console: http://localhost:9001"
echo ""
echo "Default Login:"
echo "  Email:    admin@aixp.local"
echo "  Password: admin123"
echo ""
echo "Change default password immediately!"
echo "========================================"
