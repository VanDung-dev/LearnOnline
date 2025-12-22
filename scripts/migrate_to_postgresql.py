"""
Complete migration script: SQLite → PostgreSQL
This script performs a full migration with verification
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_postgresql_connection():
    """Test PostgreSQL connection"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
    import django
    django.setup()
    
    from django.db import connection
    from django.conf import settings
    
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    
    print(f"Database Engine: {db_engine}")
    print(f"Database Name: {db_name}")
    
    if 'sqlite' in db_engine:
        print("\n⚠ Warning: DATABASE is still configured for SQLite")
        print("Please update .env to use PostgreSQL before running this script")
        print("\nTo switch to PostgreSQL:")
        print("1. Copy .env.postgresql.example to .env")
        print("2. Update PostgreSQL credentials in .env")
        print("3. Run this script again")
        return False
    
    try:
        connection.ensure_connection()
        print("\n✓ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"\n✗ PostgreSQL connection failed: {e}")
        return False


def run_migrations():
    """Run Django migrations"""
    from django.core.management import call_command
    print("\n--- Running migrations ---")
    call_command('migrate', '--verbosity', '1')
    print("✓ Migrations completed")


def verify_data_count():
    """Verify data counts after migration"""
    from django.contrib.auth.models import User
    from courses.models import Course, Category, Module, Lesson, Enrollment
    from accounts.models import Profile
    from payments.models import Payment
    
    counts = {
        'Users': User.objects.count(),
        'Profiles': Profile.objects.count(),
        'Categories': Category.objects.count(),
        'Courses': Course.objects.count(),
        'Modules': Module.objects.count(),
        'Lessons': Lesson.objects.count(),
        'Enrollments': Enrollment.objects.count(),
        'Payments': Payment.objects.count(),
    }
    
    print("\n--- Data Verification ---")
    for model, count in counts.items():
        status = "✓" if count > 0 else "○"
        print(f"  {status} {model}: {count}")
    
    return counts


def main():
    print("=" * 50)
    print("LearnOnline: SQLite → PostgreSQL Migration")
    print("=" * 50)
    
    # Step 1: Check database connection
    if not check_postgresql_connection():
        sys.exit(1)
    
    # Step 2: Run migrations
    run_migrations()
    
    # Step 3: Show data verification
    counts = verify_data_count()
    
    if all(c == 0 for c in counts.values()):
        print("\n⚠ Database is empty. Import data using:")
        print("  python scripts/db_restore.py backups/db_backup_TIMESTAMP.json")
    
    print("\n" + "=" * 50)
    print("Migration setup complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
