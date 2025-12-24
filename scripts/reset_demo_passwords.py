"""
Reset demo passwords for specific users in Django project.

Don't use this script for production environments. It's intended for development and testing purposes only.
"""

import os
import sys
import django

print("Do you want to reset demo passwords? (yes/no)")
if input().lower() != 'yes':
    print("Aborting...")
    sys.exit(0)

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.contrib.auth.models import User

# Danh sách user cần reset mật khẩu
users = [
    'admin', 
    'instructor_john', 
    'instructor_jane', 
    'student_alice', 
    'student_bob'
]

print("Starting password reset...")
for username in users:
    try:
        u = User.objects.get(username=username)
        u.set_password('password123')
        u.save()
        print(f"  [OK] Updated password for '{username}' to 'password123'")
    except User.DoesNotExist:
        print(f"  [!!] User '{username}' not found")
print("Done.")
