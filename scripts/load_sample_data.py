"""
Load sample data fixtures from scripts/sample/ directory.
Files are loaded in order based on their numeric prefix.
"""
import os
import sys
import glob

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from django.core.management import call_command

def main():
    print("=" * 50)
    print("Loading Sample Data Fixtures")
    print("=" * 50)
    
    # Get sample directory
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample')
    
    # Get all JSON files sorted by name (numeric prefix ensures correct order)
    fixture_files = sorted(glob.glob(os.path.join(sample_dir, '*.json')))
    
    if not fixture_files:
        print("No fixture files found in scripts/sample/")
        return
    
    print(f"\nFound {len(fixture_files)} fixture files")
    print("-" * 50)
    
    # Load each fixture
    for filepath in fixture_files:
        filename = os.path.basename(filepath)
        try:
            call_command('loaddata', filepath, verbosity=0)
            print(f"  [OK] {filename}")
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")
    
    print("\n" + "=" * 50)
    print("Resetting demo passwords...")
    print("=" * 50)
    
    # Reset passwords
    from django.contrib.auth.models import User
    demo_users = [
        'admin', 
        'admin_school_a', 
        'instructor_john', 
        'instructor_jane', 
        'student_alice', 
        'student_bob'
    ]
    
    for username in demo_users:
        try:
            u = User.objects.get(username=username)
            u.set_password('password123')
            u.save()
            print(f"  [OK] {username}")
        except User.DoesNotExist:
            print(f"  [!!] {username} not found")
    
    print("\n" + "=" * 50)
    print("All done! Database is ready.")
    print("All demo users have password: password123")
    print("=" * 50)

if __name__ == '__main__':
    main()
