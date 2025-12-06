# Docker Setup Guide

## ⚡ Now Using UV for Faster Builds

This project uses [uv](https://github.com/astral-sh/uv) for 10-100x faster Python package installation in Docker. See [UV_MIGRATION_GUIDE.md](UV_MIGRATION_GUIDE.md) for details.

## Quick Start

### 1. Start All Services (PostgreSQL + MongoDB + Backend)
```powershell
cd portfolio-ai-app
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5433
- MongoDB on port 27017
- Backend API on port 5000

### 2. Check Container Status
```powershell
docker-compose ps
```

### 3. View Logs
```powershell
# All services
docker-compose logs -f

# PostgreSQL only
docker-compose logs -f postgres

# Backend only
docker-compose logs -f backend
```

### 4. Initialize Database
The database will be automatically created. If you need to run migrations:
```powershell
docker-compose exec backend python init_db.py
```

### 5. Stop All Services
```powershell
docker-compose down
```

### 6. Stop and Remove All Data
```powershell
docker-compose down -v
```

### 7. Rebuild Backend After Code Changes
```powershell
docker-compose up -d --build backend
```

### 8. Development Mode (With Hot-Reloading & Enhanced Logging)
```powershell
docker-compose -f docker-compose.dev.yml up -d
```

## Service Details

### PostgreSQL Database
- **Host**: localhost (from host machine) or `postgres` (from other containers)
- **Port**: 5433
- **Database**: pythonmoneytracker
- **Username**: postgres
- **Password**: Admin@1234

### MongoDB
- **Host**: localhost (from host machine) or `mongodb` (from other containers)
- **Port**: 27017
- **Database**: receipts
- **Username**: mongouser
- **Password**: Admin@1234

### Backend API
- **URL**: http://localhost:5000
- **Swagger Docs**: http://localhost:5000/swagger
- **Health**: http://localhost:5000/health (if implemented)

## Troubleshooting

### Port Already in Use
If ports are already in use, change the port mapping in docker-compose.yml:
```yaml
# For PostgreSQL
ports:
  - "5433:5432"  # Maps to 5433 on host

# For Backend
ports:
  - "5001:5000"  # Maps to 5001 on host
```

### Check Container Health
```powershell
# PostgreSQL
docker exec pythonmoneytracker-db pg_isready -U postgres

# Backend
docker-compose exec backend curl http://localhost:5000/health
```

### Access PostgreSQL CLI
```powershell
docker exec -it pythonmoneytracker-db psql -U postgres -d pythonmoneytracker
```

### Access Backend Shell
```powershell
docker-compose exec backend /bin/bash
```

### View Backend Python Logs
```powershell
docker-compose logs -f backend --tail=100
```

### Reset Everything
```powershell
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend python init_db.py
```

### Run Backend Commands
```powershell
# Initialize database
docker-compose exec backend python init_db.py

# Create test user
docker-compose exec backend python create_test_user.py

# Run tests
docker-compose exec backend python -m pytest
```

## Development Workflow

### Option 1: Full Docker (Recommended for Production-like Testing)
```powershell
# Start everything
docker-compose up -d

# Backend code changes are auto-reloaded (volume mounted)
# View logs to see changes
docker-compose logs -f backend
```

### Option 2: Hybrid (Database in Docker, Backend Local)
```powershell
# Start only database
docker-compose up -d postgres

# Run backend locally (in another terminal)
cd backend-api
python run.py
```

## Benefits of Docker Setup

- **Isolated Environment**: Services run in their own containers
- **Easy Setup**: No manual installation of PostgreSQL, MongoDB or dependencies
- **Consistent**: Same environment across all machines
- **Persistent Data**: Data stored in Docker volumes survives container restarts
- **Easy Cleanup**: Remove everything with one command
- **Networking**: Services can communicate using service names
- **Hot Reload**: Backend code changes are automatically detected
- **⚡ Fast Builds**: UV package manager provides 10-100x faster dependency installation
- **Optimized Caching**: Layer caching and .dockerignore reduce rebuild times

## Performance with UV

Build performance improvements:
- **Fresh dependency install**: ~45s with pip → ~2-5s with uv (9-22x faster)
- **Cached builds**: ~30s with pip → ~1s with uv (30x faster)
- **Dependency resolution**: ~20s with pip → ~0.5s with uv (40x faster)

## Configuration Files

- `docker-compose.yml` - Production/standard configuration
- `docker-compose.dev.yml` - Development configuration with enhanced debugging
- `Dockerfile` - Production backend image
- `Dockerfile.dev` - Development backend image
- `pyproject.toml` - Python project configuration (modern format)
- `requirements.txt` - Python dependencies (traditional format, still supported)
