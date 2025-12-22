"""
Database restore script for LearnOnline
Restores data from JSON backup to target database
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from django.core.management import call_command
from django.conf import settings


def restore_database(backup_file: str):
    """Restore database from JSON backup"""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    # Show current database info
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    print(f"Target Database Engine: {db_engine}")
    print(f"Target Database Name: {db_name}")
    print(f"\nRestoring from: {backup_file}")
    print("Warning: This will add data to the current database!")
    
    confirm = input("\nContinue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nRestoring data...")
    call_command('loaddata', str(backup_path))
    print("\n✓ Restore completed!")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python db_restore.py <backup_file.json>")
        print("\nExample:")
        print("  python scripts/db_restore.py backups/db_backup_20231221_120000.json")
        sys.exit(1)
    
    restore_database(sys.argv[1])
