# Database Migration Guide: SQLite → PostgreSQL

## Overview

This guide explains how to migrate LearnOnline from SQLite to PostgreSQL.

## Prerequisites

- PostgreSQL 14+ installed
- Python 3.10+
- All project dependencies installed (`pip install -r requirements.txt`)

---

## Quick Start

### Step 1: Backup Current Data (SQLite)

```bash
python scripts/db_backup.py
```

This creates a backup file in `backups/` directory (e.g., `backups/db_backup_20231221_120000.json`).

### Step 2: Setup PostgreSQL

```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE learnonline_db;
CREATE USER learnonline_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE learnonline_db TO learnonline_user;

-- For PostgreSQL 15+, also run:
\c learnonline_db
GRANT ALL ON SCHEMA public TO learnonline_user;
```

### Step 3: Update Environment

```bash
# Copy PostgreSQL template
cp .env.postgresql.example .env

# Edit .env with your PostgreSQL credentials
```

### Step 4: Run Migration

```bash
python scripts/migrate_to_postgresql.py
```

### Step 5: Import Data

```bash
python scripts/db_restore.py backups/db_backup_TIMESTAMP.json
```

### Step 6: Verify

```bash
python manage.py check
python manage.py test
python manage.py runserver
```

---

## Rollback to SQLite

To rollback to SQLite:

1. Update `.env` to use SQLite settings:

   ```env
   DB_ENGINE=django.db.backends.sqlite3
   DB_NAME=db.sqlite3
   ```

2. Your SQLite database (`db.sqlite3`) remains unchanged

---

## Troubleshooting

### Connection Refused

- Verify PostgreSQL is running: `pg_isready`
- Check `DB_HOST` and `DB_PORT` in `.env`

### Permission Denied

- Ensure database user has proper permissions
- Check `pg_hba.conf` for authentication method

### Data Import Errors

- Ensure migrations are applied before importing: `python manage.py migrate`
- Check backup file is valid JSON

---

## Useful Commands

```bash
# Check Django configuration
python manage.py check --deploy

# Show migration status
python manage.py showmigrations

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```
