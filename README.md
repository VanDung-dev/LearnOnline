## Installation

1. Install required packages:

    ```bash
    pip install -r requirements.txt
    ```

2. Set up TinyMCE for rich text editing:

    ```bash
    python setup_tinymce.py
    ```

3. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

4. Create a Superuser (Admin):

    ```bash
    python manage.py createsuperuser
    ```

5. Start the development server:

    ```bash
    python manage.py runserver
    ```

---

## Troubleshooting

### Database Adaptation (Important)

If you encounter migration errors after pulling new code (or if migrations were reset), use these commands to sync your database without losing data:

**1. Standard Update:**

```bash
python manage.py migrate
```

**2. If Migrations were Reset (Squashed):**
If the migration history text files were deleted/reset but your database still has the tables, you must "fake" the initial migration:

```bash
# Ensure migration files exist
python manage.py makemigrations

# Mark as applied without modifying database tables
python manage.py migrate --fake
```

### Other Commands

If you encounter other errors, try these:

1. Show migration status:

    ```bash
    python manage.py showmigrations
    ```

2. Reset database (WARNING: DELETES ALL DATA):

    ```bash
    python manage.py flush
    ```

3. Collect static files:

    ```bash
    python manage.py collectstatic
    ```

4. Re-setup TinyMCE (if needed):

    ```bash
    python setup_tinymce.py
    ```

---

## Static Files

In production mode (`DEBUG=False`), Django requires static files to be collected into a single directory.
The `staticfiles` directory is automatically created when you run `collectstatic` command. This directory
contains all CSS, JavaScript, and image files from the project needed to run the application properly
when debug mode is disabled.

To collect static files:

```bash
python manage.py collectstatic --noinput
```
