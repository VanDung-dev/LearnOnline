"""
Migration to rename Module model to Section.

This migration:
1. Renames the courses_module table to courses_section
2. Renames the module_id foreign key in courses_lesson to section_id
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        # Step 1: Rename the Module table to Section
        migrations.RenameModel(
            old_name='Module',
            new_name='Section',
        ),
        # Step 2: Rename the foreign key field in Lesson from module to section
        migrations.RenameField(
            model_name='lesson',
            old_name='module',
            new_name='section',
        ),
        # Step 3: Update related_name - Django handles this automatically
        # when the model is renamed
    ]
