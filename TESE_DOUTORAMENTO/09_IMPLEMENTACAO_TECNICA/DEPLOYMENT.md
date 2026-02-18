# 🚀 Deployment Guide

## Running Through GitHub

### GitHub Actions (CI/CD)

Your repository includes automated workflows:

#### 1. **Backend Tests** (`backend-tests.yml`)
- Triggers on push/PR to backend files
- Sets up PostgreSQL test database
- Runs backend tests automatically

#### 2. **Frontend Build** (`frontend-build.yml`)
- Triggers on push/PR to frontend files
- Builds production frontend
- Uploads build artifacts

#### 3. **Pitch Deck Deployment** (`deploy-pitch-deck.yml`)
- Deploys pitch deck to GitHub Pages
- Accessible at: `https://refitruisantos.github.io/projeto_futebol/`

### Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Your pitch deck will deploy automatically on push

### GitHub Codespaces

Run your entire project in the cloud:

1. Click **Code** → **Codespaces** → **Create codespace on main**
2. Wait for environment to load
3. Run setup commands:

```bash
# Backend
cd TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA/frontend
npm install
npm run dev
```

## Docker Deployment

### Docker Compose (Recommended)

```bash
# From project root
cd TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA
docker-compose up -d
```

Services:
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`
- **PostgreSQL**: `localhost:5432`

### Environment Variables

Create `.env` file:

```env
# Database
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=futebol_tese
DATABASE_USER=postgres
DATABASE_PASSWORD=your_secure_password

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Cloud Deployment Options

### Option 1: Railway.app

**Backend:**
1. Connect GitHub repository
2. Select `TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA/backend`
3. Add PostgreSQL plugin
4. Set environment variables
5. Deploy

**Frontend:**
1. New service from repo
2. Select `TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA/frontend`
3. Build command: `npm run build`
4. Start command: `npm run preview`
5. Deploy

### Option 2: Vercel (Frontend) + Render (Backend)

**Frontend on Vercel:**
```bash
cd frontend
npm install -g vercel
vercel --prod
```

**Backend on Render:**
1. Connect GitHub repository
2. Root directory: `TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA/backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database

### Option 3: DigitalOcean App Platform

1. Create new app from GitHub
2. Add two components:
   - **Backend** (Python)
   - **Frontend** (Node.js)
3. Add PostgreSQL database
4. Configure environment variables
5. Deploy

### Option 4: AWS (EC2 + RDS)

**Setup:**
```bash
# Install Docker on EC2
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Clone repository
git clone https://github.com/Refitruisantos/projeto_futebol.git
cd projeto_futebol/TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA

# Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files with RDS credentials

# Run with Docker Compose
docker-compose up -d
```

## GitHub Container Registry

Build and push Docker images:

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build backend
cd backend
docker build -t ghcr.io/refitruisantos/soccer-analytics-backend:latest .
docker push ghcr.io/refitruisantos/soccer-analytics-backend:latest

# Build frontend
cd ../frontend
docker build -t ghcr.io/refitruisantos/soccer-analytics-frontend:latest .
docker push ghcr.io/refitruisantos/soccer-analytics-frontend:latest
```

## Production Checklist

### Security
- [ ] Change default database password
- [ ] Use HTTPS (SSL certificate)
- [ ] Configure CORS for production domains only
- [ ] Set secure session cookies
- [ ] Enable rate limiting
- [ ] Sanitize file uploads

### Performance
- [ ] Enable PostgreSQL connection pooling
- [ ] Configure Redis for caching
- [ ] Use CDN for static assets
- [ ] Minify and compress frontend assets
- [ ] Enable gzip compression

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure application logging
- [ ] Set up uptime monitoring
- [ ] Database backup automation
- [ ] Performance monitoring (New Relic/DataDog)

### Database
- [ ] Run migrations in production
- [ ] Set up automated backups
- [ ] Configure replication (optional)
- [ ] Optimize indexes
- [ ] Set up monitoring

## Environment-Specific Configuration

### Development
```env
DEBUG=true
LOG_LEVEL=debug
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Staging
```env
DEBUG=false
LOG_LEVEL=info
CORS_ORIGINS=https://staging.yourdomain.com
DATABASE_NAME=futebol_tese_staging
```

### Production
```env
DEBUG=false
LOG_LEVEL=warning
CORS_ORIGINS=https://yourdomain.com
DATABASE_NAME=futebol_tese_production
ENABLE_METRICS=true
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (Nginx/HAProxy)
- Multiple backend instances
- Shared PostgreSQL instance
- Redis for session storage

### Database Scaling
- Read replicas for analytics queries
- Connection pooling (PgBouncer)
- Partitioning for large tables
- Regular VACUUM and ANALYZE

### File Storage
- Use S3/MinIO for video files
- CDN for static assets
- Separate storage service from app servers

## Backup Strategy

### Automated Backups
```bash
# PostgreSQL backup (add to cron)
pg_dump -U postgres futebol_tese > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup to S3
aws s3 cp backup_*.sql s3://your-bucket/backups/
```

### Disaster Recovery
1. Daily automated backups
2. Weekly full backups
3. Keep 30 days of backups
4. Test restore procedure monthly
5. Replicate to different region

## Troubleshooting Production Issues

### Backend Not Starting
```bash
# Check logs
docker logs soccer-analytics-backend

# Check database connection
docker exec -it postgres psql -U postgres -d futebol_tese
```

### Frontend Build Fails
```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Database Connection Issues
- Verify credentials in `.env`
- Check PostgreSQL is running
- Verify network connectivity
- Check firewall rules

---

**For local development setup**, see [SETUP.md](SETUP.md)

**For GitHub push instructions**, see [GITHUB_PUSH.md](GITHUB_PUSH.md)
