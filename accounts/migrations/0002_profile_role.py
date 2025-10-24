from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('student', 'Student'), ('instructor', 'Instructor'), ('admin', 'Admin')], default='student', max_length=20),
        ),
    ]
