# Deployment Guide

This guide covers deploying the Deepfake Detection Platform to production environments.

## 🚀 Production Deployment Options

### Option 1: Docker Compose (Recommended for Small-Medium Scale)

#### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Docker & Docker Compose installed
- Domain name (optional, for HTTPS)
- 2GB+ RAM, 20GB+ disk space

#### Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd deepfake-detection-platform
```

2. **Configure environment variables**
```bash
cd backend
cp .env.example .env
nano .env
```

Update the following:
```env
DATABASE_URL=postgresql://deepfake_user:STRONG_PASSWORD_HERE@postgres:5432/deepfake_db
SECRET_KEY=GENERATE_LONG_RANDOM_STRING_HERE
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **Update docker-compose.yml for production**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: deepfake-postgres
    environment:
      POSTGRES_USER: deepfake_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # Use env variable
      POSTGRES_DB: deepfake_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - deepfake-network

  backend:
    build: ./backend
    container_name: deepfake-backend
    environment:
      DATABASE_URL: postgresql://deepfake_user:${POSTGRES_PASSWORD}@postgres:5432/deepfake_db
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 60
    volumes:
      - ./backend/uploads:/app/uploads
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - deepfake-network

  nginx:
    image: nginx:alpine
    container_name: deepfake-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - deepfake-network

volumes:
  postgres_data:

networks:
  deepfake-network:
    driver: bridge
```

4. **Build frontend for production**
```bash
cd frontend
npm install
npm run build
```

5. **Configure Nginx**

Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect to HTTPS (uncomment when SSL is configured)
        # return 301 https://$server_name$request_uri;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API Documentation
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        # File uploads
        client_max_body_size 10M;
    }

    # HTTPS configuration (uncomment when SSL is configured)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #
    #     location / {
    #         root /usr/share/nginx/html;
    #         try_files $uri $uri/ /index.html;
    #     }
    #
    #     location /api {
    #         proxy_pass http://backend;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #     }
    # }
}
```

6. **Start services**
```bash
docker-compose up -d
```

7. **Verify deployment**
```bash
docker-compose ps
curl http://localhost/api/health
```

### Option 2: Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- kubectl configured
- Helm (optional)

#### Kubernetes Manifests

Create `k8s/namespace.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: deepfake-detection
```

Create `k8s/postgres.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: deepfake-detection
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: deepfake-detection
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
        - name: POSTGRES_USER
          value: deepfake_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: POSTGRES_DB
          value: deepfake_db
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: deepfake-detection
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

Create `k8s/backend.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: deepfake-detection
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
        image: your-registry/deepfake-backend:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: jwt-secret
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: deepfake-detection
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
```

Create secrets:
```bash
kubectl create secret generic db-secret \
  --from-literal=password=YOUR_DB_PASSWORD \
  --from-literal=url=postgresql://deepfake_user:YOUR_DB_PASSWORD@postgres:5432/deepfake_db \
  -n deepfake-detection

kubectl create secret generic app-secret \
  --from-literal=jwt-secret=YOUR_JWT_SECRET \
  -n deepfake-detection
```

Deploy:
```bash
kubectl apply -f k8s/
```

### Option 3: Cloud Platform Deployment

#### AWS (Elastic Beanstalk + RDS)

1. **Create RDS PostgreSQL instance**
2. **Create Elastic Beanstalk application**
3. **Configure environment variables**
4. **Deploy using EB CLI**

```bash
eb init
eb create production
eb deploy
```

#### Google Cloud Platform (Cloud Run + Cloud SQL)

1. **Build and push Docker image**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/deepfake-backend
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy deepfake-backend \
  --image gcr.io/PROJECT_ID/deepfake-backend \
  --platform managed \
  --region us-central1 \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME
```

#### Azure (App Service + Azure Database)

1. **Create Azure Database for PostgreSQL**
2. **Create App Service**
3. **Deploy using Azure CLI**

```bash
az webapp up --name deepfake-detection --runtime "PYTHON:3.10"
```

## 🔒 Security Hardening

### 1. HTTPS/SSL Configuration

#### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 2. Environment Variables

Never commit sensitive data. Use:
- Docker secrets
- Kubernetes secrets
- Cloud provider secret managers (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)

### 3. Database Security

```sql
-- Create read-only user for reporting
CREATE USER readonly_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE deepfake_db TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Enable SSL connections
ALTER SYSTEM SET ssl = on;
```

### 4. Rate Limiting

Add to Nginx configuration:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://backend;
}
```

### 5. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📊 Monitoring & Logging

### 1. Application Monitoring

#### Using Prometheus + Grafana

Create `docker-compose.monitoring.yml`:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
```

### 2. Log Aggregation

#### Using ELK Stack

```bash
docker run -d --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  elasticsearch:8.11.0

docker run -d --name kibana \
  -p 5601:5601 \
  --link elasticsearch:elasticsearch \
  kibana:8.11.0
```

### 3. Health Checks

Add to `docker-compose.yml`:
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 🔄 Backup & Recovery

### Database Backup

#### Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/deepfake_db_$DATE.sql"

# Create backup
docker-compose exec -T postgres pg_dump -U deepfake_user deepfake_db > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Delete backups older than 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### Restore from Backup

```bash
gunzip backup.sql.gz
docker-compose exec -T postgres psql -U deepfake_user deepfake_db < backup.sql
```

### File Backup

```bash
# Backup uploads directory
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/

# Restore
tar -xzf uploads_backup_20240130.tar.gz
```

## 📈 Scaling

### Horizontal Scaling

#### Backend Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

#### Load Balancing with Nginx

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

### Database Scaling

#### Read Replicas

```yaml
services:
  postgres-replica:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: deepfake_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: deepfake_db
      POSTGRES_MASTER_SERVICE_HOST: postgres
```

## 🧪 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t deepfake-backend:${{ github.sha }} ./backend

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push deepfake-backend:${{ github.sha }}

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/deepfake-detection-platform
            docker-compose pull
            docker-compose up -d
```

## 📞 Production Checklist

- [ ] Environment variables configured
- [ ] HTTPS/SSL enabled
- [ ] Database backups automated
- [ ] Monitoring and alerting set up
- [ ] Rate limiting configured
- [ ] Firewall rules applied
- [ ] Log aggregation configured
- [ ] Health checks enabled
- [ ] CI/CD pipeline set up
- [ ] Documentation updated
- [ ] Security audit completed
- [ ] Load testing performed
- [ ] Disaster recovery plan documented

## 🆘 Troubleshooting Production Issues

### High Memory Usage

```bash
# Check container memory
docker stats

# Increase memory limits
docker-compose up -d --scale backend=2
```

### Database Connection Pool Exhausted

Update `backend/app/core/database.py`:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```

### Slow API Response

```bash
# Enable query logging
docker-compose exec postgres psql -U deepfake_user -d deepfake_db
ALTER DATABASE deepfake_db SET log_statement = 'all';
```

---

**Production deployment complete! Monitor your application and scale as needed.** 🚀
