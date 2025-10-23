# Docker Setup for LearnOnline

This directory contains the Docker configuration for the LearnOnline Django project.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Build and run the containers:
   ```
   docker-compose up --build
   ```

2. Access the application at http://localhost:8000

## Commands

- To run in detached mode:
  ```
  docker-compose up -d
  ```

- To stop the containers:
  ```
  docker-compose down
  ```

- To view logs:
  ```
  docker-compose logs
  ```

- To run Django management commands:
  ```
  docker-compose exec web python manage.py migrate
  docker-compose exec web python manage.py createsuperuser
  ```

## Project Structure

- `Dockerfile`: Defines the Django application container
- `docker-compose.yml`: Defines the application services
- `../DjangoProject/settings_docker.py`: Django settings for Docker environment

## Environment Variables

The following environment variables can be configured in the `docker-compose.yml`:

- `DEBUG`: Django debug mode (default: 1)
- `SECRET_KEY`: Django secret key
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

## Troubleshooting

### Windows Users

If you encounter issues with Docker on Windows:

1. Make sure Docker Desktop is installed and running
2. If using PowerShell, use `;` instead of `&&` to chain commands:
   ```
   cd docker; docker-compose up -d
   ```
3. Ensure that Docker Desktop is configured to use Linux containers

### Common Issues

1. Port already in use:
   - Change the port mapping in docker-compose.yml
   - Stop other services using port 8000

2. Permission denied:
   - Make sure Docker daemon is running
   - Try running the terminal as administrator (on Windows)