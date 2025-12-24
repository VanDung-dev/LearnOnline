# Docker Setup for LearnOnline

This directory contains the Docker configuration for the LearnOnline Django project.

## Prerequisites

- Docker
- Docker Compose

## Installation

Follow these steps to get the application running completely.

1. **Build and Start the containers:**
    This command builds the images and starts the services in detached mode (background).

    ```bash
    docker-compose up --build -d
    ```

2. **Apply Database Migrations:**  
    This ensures your database tables are created according to the latest code.

    ```bash
    docker-compose exec web python manage.py migrate
    ```

3. **Create a Superuser (Admin):**  
    You need an admin account to manage the application and access the admin panel.

    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

    *Follow the prompts in the terminal to set your username, email, and password.*

4. **Access the Application:**
    - **Main Site:** [http://localhost:8000](http://localhost:8000)
    - **Admin Panel:** [http://localhost:8000/admin](http://localhost:8000/admin)

## Common Commands

- **Stop containers:**

  ```bash
  docker-compose down
  ```

- **View logs (follow mode):**

  ```bash
  docker-compose logs -f
  ```

- **Open a shell inside the container:**

  ```bash
  docker-compose exec web /bin/bash
  ```

## Troubleshooting

### Database Adaptation (After Updates)

When you pull new code or switch branches, the database schema might be out of sync.

**1. Apply Standard Updates:**
If the update contains new migration files, simply run:

```bash
docker-compose exec web python manage.py migrate
```

**2. Handling Migration Conflicts or Resets:**
If the migration history was reset (e.g., all migrations squashed to `0001_initial.py`) but your database still contains the old tables, you must "fake" the migration to sync the history without touching the tables:

```bash
# Step 1: Ensure migration files are generated (if missing)
docker-compose exec web python manage.py makemigrations

# Step 2: Mark migrations as applied without running SQL
docker-compose exec web python manage.py migrate --fake
```

### Windows Issues

1. **PowerShell Syntax:**
    Use `;` instead of `&&` to chain commands.

    ```powershell
    cd docker; docker-compose up -d
    ```

2. **Volume Permissions:**
    If you see "Permission denied" errors, ensure Docker Desktop is running and try running your terminal as Administrator.

### General Issues

1. **Port 8000 already in use:**
    - Stop other services using port 8000.
    - Or change the port mapping in `docker-compose.yml` (e.g., `"8080:8000"`).

2. **Container exits immediately:**
    Check the logs to find the error:

    ```bash
    docker-compose logs web
    ```
