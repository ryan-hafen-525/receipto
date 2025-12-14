# Docker Commands for Reciepto

This guide provides essential Docker commands for working with the Reciepto application.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose V2
- At least 4GB of available RAM
- Ports 3000, 8000, 5432, 8080, 8333, 8888, 9333 must be available

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your API keys
nano .env

# 3. Build all services
docker compose build

# 4. Start all services in background
docker compose up -d

# 5. Check status
docker compose ps

# 6. View logs
docker compose logs -f
```

## Production Build and Run

### Build Services

```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend

# Build without cache (clean build)
docker compose build --no-cache
```

### Start Services

```bash
# Start all services in foreground
docker compose up

# Start all services in background (detached mode)
docker compose up -d

# Start specific service
docker compose up backend

# Start and rebuild if needed
docker compose up --build
```

### Stop Services

```bash
# Stop all services (containers remain)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers, volumes (WARNING: deletes data)
docker compose down -v

# Stop and remove containers, volumes, and images
docker compose down -v --rmi all
```

### View Logs

```bash
# View logs from all services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs from specific service
docker compose logs backend
docker compose logs frontend

# View last 100 lines and follow
docker compose logs --tail=100 -f backend

# View logs with timestamps
docker compose logs -t
```

## Development Mode

Development mode enables hot reload for both frontend and backend.

### Start Development Environment

```bash
# Start with development overrides
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Start in background
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Rebuild and start
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Development Workflow

```bash
# Make changes to code (auto-reloads)
# Frontend: Changes in ./frontend auto-reload
# Backend: Changes in ./api auto-reload

# Rebuild specific service after dependency changes
docker compose -f docker-compose.yml -f docker-compose.dev.yml build backend
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend

# View development logs
docker compose logs -f backend frontend
```

## Service Management

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

### Execute Commands in Running Container

```bash
# Access backend shell
docker compose exec backend bash

# Access frontend shell
docker compose exec frontend sh

# Run Python script in backend
docker compose exec backend python script.py

# Run npm command in frontend
docker compose exec frontend npm run lint
```

### View Resource Usage

```bash
# View stats for all containers
docker compose stats

# View stats for specific service
docker stats receipto-backend
```

### Inspect Service

```bash
# View service configuration
docker compose config

# View specific service config
docker compose config backend

# Validate docker-compose file
docker compose config --quiet
```

## Database Operations

### Connect to PostgreSQL

```bash
# Connect to database
docker compose exec db psql -U receipto -d receipto

# Run SQL query directly
docker compose exec db psql -U receipto -d receipto -c "SELECT COUNT(*) FROM categories;"

# List all tables
docker compose exec db psql -U receipto -d receipto -c "\dt"
```

### Backup Database

```bash
# Create backup
docker compose exec db pg_dump -U receipto receipto > backup_$(date +%Y%m%d_%H%M%S).sql

# Create compressed backup
docker compose exec db pg_dump -U receipto receipto | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restore Database

```bash
# Restore from backup
docker compose exec -T db psql -U receipto receipto < backup.sql

# Restore from compressed backup
gunzip < backup.sql.gz | docker compose exec -T db psql -U receipto receipto
```

### Reset Database

```bash
# WARNING: This will delete all data

# 1. Stop services
docker compose down

# 2. Remove database volume
docker volume rm receipto-postgres-data

# 3. Start services (will recreate and reinitialize)
docker compose up -d
```

## SeaweedFS Operations

### Check Cluster Status

```bash
# Check cluster health
curl http://localhost:9333/cluster/status

# Check volume server status
curl http://localhost:8080/status

# Check filer status
curl http://localhost:8888/
```

### S3 API Operations

You can use AWS CLI or any S3-compatible client:

```bash
# Configure AWS CLI for SeaweedFS
aws configure set aws_access_key_id seaweed_admin
aws configure set aws_secret_access_key seaweed_secret_dev
aws configure set default.region us-east-1

# Create bucket
aws s3 --endpoint-url http://localhost:8333 mb s3://receipts

# Upload file
aws s3 --endpoint-url http://localhost:8333 cp receipt.jpg s3://receipts/

# List files
aws s3 --endpoint-url http://localhost:8333 ls s3://receipts/

# Download file
aws s3 --endpoint-url http://localhost:8333 cp s3://receipts/receipt.jpg ./downloaded.jpg

# Delete file
aws s3 --endpoint-url http://localhost:8333 rm s3://receipts/receipt.jpg
```

### Using Python boto3

```python
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:8333',
    aws_access_key_id='seaweed_admin',
    aws_secret_access_key='seaweed_secret_dev',
    region_name='us-east-1'
)

# Upload file
s3.upload_file('receipt.jpg', 'receipts', 'receipt.jpg')

# List objects
response = s3.list_objects_v2(Bucket='receipts')
for obj in response.get('Contents', []):
    print(obj['Key'])
```

## Health Checks

### Check All Services

```bash
# View health status
docker compose ps

# Services should show "(healthy)" in STATUS column
```

### Manual Health Checks

```bash
# Frontend
curl http://localhost:3000

# Backend API
curl http://localhost:8000/health

# Backend API docs
curl http://localhost:8000/docs

# Database
docker compose exec db pg_isready -U receipto

# SeaweedFS Master
curl http://localhost:9333/cluster/status

# SeaweedFS Volume
curl http://localhost:8080/status

# SeaweedFS Filer
curl http://localhost:8888/

# SeaweedFS S3
curl http://localhost:8333/
```

## Troubleshooting

### View Service Logs

```bash
# Check for errors in backend
docker compose logs backend | grep -i error

# Check for errors in frontend
docker compose logs frontend | grep -i error

# Check database logs
docker compose logs db
```

### Rebuild Service

```bash
# Rebuild without cache
docker compose build --no-cache backend

# Restart service
docker compose up -d backend
```

### Fix Port Conflicts

```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill process using the port
kill -9 <PID>

# Or change port in .env
echo "POSTGRES_PORT=5433" >> .env
```

### Fix Permission Issues

```bash
# Reset permissions
docker compose down
sudo chown -R $USER:$USER ./api ./frontend
docker compose up -d
```

### Clear Everything and Restart

```bash
# Nuclear option: remove everything and start fresh
docker compose down -v
docker system prune -af --volumes
docker compose up --build -d
```

## Cleanup

### Remove Stopped Containers

```bash
# Remove stopped containers for this project
docker compose rm -f

# Remove all stopped containers
docker container prune
```

### Remove Unused Images

```bash
# Remove dangling images
docker image prune

# Remove all unused images
docker image prune -a

# Remove specific image
docker rmi receipto-backend
docker rmi receipto-frontend
```

### Remove Unused Volumes

```bash
# Remove unused volumes
docker volume prune

# Remove specific volume (WARNING: deletes data)
docker volume rm receipto-postgres-data
docker volume rm receipto-seaweedfs-volume
```

### Complete Cleanup

```bash
# WARNING: This removes ALL Docker resources (not just Reciepto)

# Remove everything
docker system prune -af --volumes

# Remove project-specific resources only
docker compose down -v
docker volume rm receipto-postgres-data receipto-seaweedfs-master receipto-seaweedfs-volume receipto-seaweedfs-filer
docker network rm receipto-network
```

## Performance Monitoring

### Monitor Resource Usage

```bash
# Real-time stats
docker compose stats

# Check disk usage
docker system df

# Check specific volume size
docker volume inspect receipto-postgres-data
```

### Limit Resources

Add to docker-compose.yml under a service:

```yaml
services:
  backend:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

## Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# Reciepto Docker aliases
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dclogs='docker compose logs -f'
alias dcps='docker compose ps'
alias dcbuild='docker compose build'
alias dcrestart='docker compose restart'

# Reciepto development
alias dcdev='docker compose -f docker-compose.yml -f docker-compose.dev.yml up'
alias dcdevup='docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d'

# Quick access
alias receipto-backend='docker compose exec backend bash'
alias receipto-frontend='docker compose exec frontend sh'
alias receipto-db='docker compose exec db psql -U receipto -d receipto'
```

## Next Steps

- Review [README.md](README.md) for application usage
- Review [SPEC.md](SPEC.md) for technical details
- Review [CLAUDE.md](CLAUDE.md) for development guidelines

## Support

For issues specific to:
- **Docker configuration**: Review this document
- **Application features**: See [README.md](README.md)
- **Implementation details**: See [SPEC.md](SPEC.md)
- **Development workflow**: See [CLAUDE.md](CLAUDE.md)
