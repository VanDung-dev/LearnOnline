import os
import sys
import django

# Setup path to import apps
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from apps.courses.models import Section, Subsection, Lesson

def run():
    print("Migrating Lessons to Subsections...")
    sections = Section.objects.all()
    count = 0
    total_lessons_moved = 0
    
    for section in sections:
        # Create default subsection if it doesn't exist
        sub, created = Subsection.objects.get_or_create(
            section=section,
            title="Part 1",
            defaults={'order': 1}
        )
        if created:
            print(f"Created subsection for Section: {section.title}")
        
        # Move lessons that don't have a subsection yet
        lessons = Lesson.objects.filter(section=section, subsection__isnull=True)
        updated = lessons.update(subsection=sub)
        
        if updated > 0:
            print(f"  Moved {updated} lessons to {sub.title}")
            total_lessons_moved += updated
        count += 1

    print(f"Processed {count} sections.")
    print(f"Total lessons migrated: {total_lessons_moved}")

if __name__ == '__main__':
    run()
