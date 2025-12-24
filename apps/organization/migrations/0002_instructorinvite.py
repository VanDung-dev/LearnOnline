from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InstructorInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('token', models.CharField(db_index=True, max_length=64, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('revoked', 'Revoked')], default='pending', max_length=20)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instructor_invites_sent', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='organization.school')),
            ],
            options={
                'db_table': 'organization_instructor_invite',
            },
        ),
        migrations.AddIndex(
            model_name='instructorinvite',
            index=models.Index(fields=['email'], name='organizati_email_c8f0dc_idx'),
        ),
        migrations.AddIndex(
            model_name='instructorinvite',
            index=models.Index(fields=['token'], name='organizati_token_0d3f07_idx'),
        ),
    ]
