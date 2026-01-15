from django.core.management.base import BaseCommand
from apps.courses.models import Section, Subsection

class Command(BaseCommand):
    help = 'Migrate existing lessons to default subsections'

    def handle(self, *args, **options):
        # Iterate over all sections that have lessons without a subsection
        sections = Section.objects.all()
        migrated_count = 0
        
        for section in sections:
            # Find lessons in this section that do not have a subsection
            lessons = section.lessons.filter(subsection__isnull=True).order_by('order')
            
            if lessons.exists():
                self.stdout.write(f'Processing section: {section.title}...')
                
                # Check if a "Default" or "General" subsection already exists
                default_subsection = section.subsections.filter(title="General").first()
                if not default_subsection:
                    # Get order for new subsection (append to end)
                    last_subsection = section.subsections.order_by('-order').first()
                    new_order = (last_subsection.order + 1) if last_subsection else 0
                    
                    default_subsection = Subsection.objects.create(
                        section=section,
                        title="General",
                        description="Automatically created for existing lessons.",
                        order=new_order
                    )
                    self.stdout.write(f'  Created subsection "General" for section {section.id}')

                # Move lessons
                for index, lesson in enumerate(lessons):
                    lesson.subsection = default_subsection
                    existing_count = default_subsection.lessons.count()

                    lesson.order = existing_count
                    lesson.order = existing_count + index

                    lesson.save()
                    migrated_count += 1
                    
        self.stdout.write(self.style.SUCCESS(f'Successfully migrated {migrated_count} lessons to subsections.'))
