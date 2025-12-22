"""
Database backup script for LearnOnline
Creates JSON backup of all data from current database
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from django.core.management import call_command
from django.conf import settings


def backup_database():
    """Create a JSON backup of the database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = PROJECT_ROOT / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f'db_backup_{timestamp}.json'
    
    # Show current database info
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    print(f"Database Engine: {db_engine}")
    print(f"Database Name: {db_name}")
    print(f"\nCreating backup: {backup_file}")
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            exclude=['contenttypes', 'auth.Permission', 'sessions'],
            stdout=f
        )
    
    file_size = backup_file.stat().st_size
    print(f"\n✓ Backup completed: {backup_file}")
    print(f"  File size: {file_size / 1024:.2f} KB")
    
    return backup_file


if __name__ == '__main__':
    backup_database()
