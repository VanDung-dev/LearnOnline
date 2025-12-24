from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.SlugField(max_length=50, unique=True)),
                ('domain', models.CharField(help_text='Email domain, e.g. hcmus.edu.vn', max_length=255, unique=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='school_logos/')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'School',
                'verbose_name_plural': 'Schools',
                'db_table': 'organization_school',
            },
        ),
    ]
