"""
Load sample data fixtures from scripts/sample/ directory.
Files are loaded in order based on their numeric prefix.
"""
import os
import sys
import glob
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from django.core.management import call_command


def copy_course_thumbnails():
    """Copy course thumbnail images from scripts/imgs to media/course_thumbnails/"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    imgs_dir = os.path.join(script_dir, 'imgs')
    project_root = os.path.dirname(script_dir)
    thumbnails_dir = os.path.join(project_root, 'media', 'course_thumbnails')

    # Create destination directory if it doesn't exist
    os.makedirs(thumbnails_dir, exist_ok=True)

    # Copy all images from imgs directory
    if os.path.exists(imgs_dir):
        copied_count = 0
        for img_file in os.listdir(imgs_dir):
            src = os.path.join(imgs_dir, img_file)
            dst = os.path.join(thumbnails_dir, img_file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                copied_count += 1
        return copied_count
    return 0


def main():
    print("=" * 50)
    print("Loading Sample Data Fixtures")
    print("=" * 50)

    # Copy course thumbnails first
    print("\nCopying course thumbnails...")
    copied = copy_course_thumbnails()
    print(f"  [OK] Copied {copied} thumbnail images")
    
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
