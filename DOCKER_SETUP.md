# Docker Setup Guide

## Quick Start

### 1. Start All Services (PostgreSQL + Backend)
```powershell
cd portfolio-ai-app
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
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

## Service Details

### PostgreSQL Database
- **Host**: localhost (from host machine) or `postgres` (from other containers)
- **Port**: 5432
- **Database**: pythonmoneytracker
- **Username**: postgres
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
- **Easy Setup**: No manual installation of PostgreSQL or dependencies
- **Consistent**: Same environment across all machines
- **Persistent Data**: Data stored in Docker volumes survives container restarts
- **Easy Cleanup**: Remove everything with one command
- **Networking**: Services can communicate using service names
- **Hot Reload**: Backend code changes are automatically detected
