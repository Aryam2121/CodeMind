# 🚀 Production Deployment Guide

## Overview

This guide covers deploying Universal AI Workspace to production environments.

## Deployment Options

### 1. Docker Compose (Small Scale)
### 2. Kubernetes (Medium to Large Scale)
### 3. Cloud Platforms (AWS, Azure, GCP)

---

## Option 1: Docker Compose Deployment

Best for: Small teams, single server deployments

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Docker & Docker Compose installed
- Domain name pointed to your server
- SSL certificate (Let's Encrypt)

### Steps

1. **Clone repository on server**

```bash
git clone <your-repo>
cd universal-ai-workspace
```

2. **Set up production environment**

```bash
# Backend
cd backend
cp .env.example .env
nano .env  # Edit with production values
```

Important production settings:
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://user:password@postgres:5432/universal_ai
OPENAI_API_KEY=<your-key>
CORS_ORIGINS=https://yourdomain.com
```

```bash
# Frontend
cd ../frontend
cp .env.example .env.local
nano .env.local
```

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

3. **Create production docker-compose**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: universal_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - app-network

  chromadb:
    image: chromadb/chroma:latest
    restart: always
    volumes:
      - chromadb_data:/chroma/chroma
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/universal_ai
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
      - DEBUG=False
    depends_on:
      - postgres
      - redis
      - chromadb
    networks:
      - app-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    depends_on:
      - backend
    networks:
      - app-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"

  traefik:
    image: traefik:v2.10
    restart: always
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "letsencrypt:/letsencrypt"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  chromadb_data:
  letsencrypt:
```

4. **Create production Dockerfiles**

`backend/Dockerfile.prod`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001"]
```

`frontend/Dockerfile.prod`:
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

ENV NODE_ENV=production
EXPOSE 3000

CMD ["npm", "start"]
```

5. **Deploy**

```bash
# Create .env file with secrets
nano .env

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f

# Run database migrations
docker-compose exec backend alembic upgrade head
```

6. **Set up monitoring**

```bash
# Install monitoring tools
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## Option 2: Kubernetes Deployment

Best for: Large scale, high availability

### Prerequisites

- Kubernetes cluster (EKS, GKE, AKS)
- kubectl configured
- Helm installed

### Steps

1. **Create namespace**

```bash
kubectl create namespace universal-ai
```

2. **Deploy PostgreSQL (or use managed service)**

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: universal-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: universal_ai
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
```

3. **Deploy backend**

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: universal-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/universal-ai-backend:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: openai-key
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
```

4. **Deploy frontend**

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: universal-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/universal-ai-frontend:latest
        env:
        - name: NEXT_PUBLIC_API_URL
          value: https://api.yourdomain.com
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

5. **Set up ingress**

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: universal-ai-ingress
  namespace: universal-ai
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    kubernetes.io/ingress.class: nginx
spec:
  tls:
  - hosts:
    - yourdomain.com
    - api.yourdomain.com
    secretName: universal-ai-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8001
```

6. **Deploy all resources**

```bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get pods -n universal-ai
kubectl get svc -n universal-ai
kubectl get ingress -n universal-ai
```

---

## Option 3: Cloud Platform Deployment

### AWS Deployment

**Services Used:**
- **ECS/EKS**: Container orchestration
- **RDS**: PostgreSQL database
- **ElastiCache**: Redis
- **S3**: File storage
- **CloudFront**: CDN
- **ALB**: Load balancing
- **Route 53**: DNS

### Azure Deployment

**Services Used:**
- **Azure Container Instances/AKS**
- **Azure Database for PostgreSQL**
- **Azure Cache for Redis**
- **Azure Blob Storage**
- **Azure CDN**
- **Application Gateway**

### GCP Deployment

**Services Used:**
- **Cloud Run/GKE**
- **Cloud SQL**
- **Memorystore**
- **Cloud Storage**
- **Cloud CDN**
- **Cloud Load Balancing**

---

## Post-Deployment Checklist

### Security

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Environment variables secured (not in code)
- [ ] Database backups configured
- [ ] Firewall rules configured
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Secrets management (Vault, AWS Secrets Manager)

### Monitoring

- [ ] Application logs centralized
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic, Datadog)
- [ ] Uptime monitoring
- [ ] Database monitoring
- [ ] Cost monitoring

### Performance

- [ ] CDN configured for static assets
- [ ] Database connection pooling
- [ ] Redis caching enabled
- [ ] Auto-scaling configured
- [ ] Load testing completed

### Backup & Recovery

- [ ] Database automated backups
- [ ] Vector database backups
- [ ] File storage backups
- [ ] Disaster recovery plan
- [ ] Backup restoration tested

---

## Maintenance

### Regular Tasks

**Daily:**
- Check error logs
- Monitor performance metrics
- Check uptime status

**Weekly:**
- Review security logs
- Check backup status
- Update dependencies (security patches)

**Monthly:**
- Full system audit
- Performance optimization
- Cost review
- Capacity planning

### Updating Application

```bash
# 1. Pull latest code
git pull origin main

# 2. Build new images
docker-compose build

# 3. Run tests
docker-compose run backend pytest

# 4. Deploy with zero downtime
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend

# 5. Verify deployment
curl https://api.yourdomain.com/health
```

---

## Troubleshooting

### Common Issues

**Backend not starting:**
```bash
docker-compose logs backend
# Check database connection
# Verify environment variables
```

**Database connection errors:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres
# Test connection
docker-compose exec backend python -c "from app.db.session import engine; print(engine.connect())"
```

**High memory usage:**
```bash
# Check container stats
docker stats
# Scale down replicas if needed
docker-compose up -d --scale backend=2
```

---

## Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- GitHub Issues
- Community discussions

---

**Remember: Always test in staging before deploying to production!**
