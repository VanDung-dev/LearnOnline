## Installation

1. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

2. Apply database migrations:
    ```bash
    python manage.py migrate
    ```

3. Start the development server:
    ```bash
    python manage.py runserver
    ```

---

## Troubleshooting

If you encounter errors, try these commands:

1. Show migration status:
    ```bash
    python manage.py showmigrations
    ```

2. Create new migrations after model changes:
    ```bash
    python manage.py makemigrations
    ```

3. Reset database (use with caution):
    ```bash
    python manage.py flush
    ```

4. Collect static files:
    ```bash
    python manage.py collectstatic
    ```