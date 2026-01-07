# Docker Setup for LearnOnline

This directory contains the Docker configuration for the LearnOnline Django project.
It supports two environments:

1. **Development (`docker-compose.yml`)**: For local development.
2. **Production Simulation (`docker-compose.prod.yml`)**: For testing real-world performance (Nginx, Gunicorn, HTTPS).

---

## 🏗 1. Build & Run

### A. Development (Dev)

For coding and debugging with hot-reload.

```bash
cd docker
docker-compose up --build -d
```

### B. Production Simulation (Prod)

For load testing and verifying deployment architecture.
**Features:**

- **Nginx** (Reverse Proxy & Static Files)
- **Gunicorn** (Production WSGI Server, multi-worker)
- **HTTPS** (Self-signed certificate)
- **PostgreSQL 15**

**Start Command:**

```powershell
# From project root
docker compose -f docker/docker-compose.prod.yml up --build -d
```

**Initialize Data (First Run Only):**
Since Production uses a separate database volume (`postgres_data_prod`), you must load data:

```powershell
# 1. Migrate DB
docker compose -f docker/docker-compose.prod.yml exec web python manage.py migrate

# 2. Load Sample Data (Optional)
docker compose -f docker/docker-compose.prod.yml exec web python manage.py loaddata sample_data.json

# 3. Create Admin Account
docker compose -f docker/docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## ⚙️ 2. Configuration & Access

- **Development URL**: `http://localhost:8000`
- **Production URL**: `https://localhost` (Accept the self-signed certificate warning)
- **Admin Panel**: `/admin/`

**Key Configuration Files:**

- `docker/Dockerfile`: Builds the Python/Django image.
- `docker/nginx/default.conf`: Nginx configuration (HTTPS, Static files).
- `docker/docker-compose.prod.yml`: Define Prod services (Web, Nginx, DB, Redis).

---

## 🧪 3. Load Testing (Chịu tải) with Locust

We use **Locust** to simulate thousands of users accessing the site.

**Prerequisite:**

- Install Locust: `pip install locust` (in a separate venv is recommended)
- **Note:** Ensure `locustfile.py` has `urllib3.disable_warnings` if testing HTTPS self-signed.

**Running Load Test:**

```powershell
# Run Locust in Headless mode (CLI only)
# --users: Total concurrent users
# --spawn-rate: Users added per second
# --host: Target URL (Use https://localhost for Prod)

.venv\Scripts\locust --headless --users 2000 --spawn-rate 50 --run-time 60s --host https://localhost
```

**Cause:** Django 5.x requires modern Postgres.
**Fix:** Ensure `docker-compose.yml` uses `image: postgres:15`.
If you upgraded from version 13, you MUST delete the old volume:

```bash
docker compose -f docker/docker-compose.prod.yml down -v
```

### 3. `ConnectionRefusedError` (Locust)

**Cause:** Server is overwhelmed or not running.
**Fix:**

- Check logs: `docker compose -f docker/docker-compose.prod.yml logs web`
- Reduce user count if testing Dev server.
- Ensure containers are up: `docker ps`

### 4. `SSL: WRONG_VERSION_NUMBER`

**Cause:** Testing HTTP target with HTTPS client or vice versa.
**Fix:** Check `--host` parameter. Use `http://` for Dev and `https://` for Prod.
