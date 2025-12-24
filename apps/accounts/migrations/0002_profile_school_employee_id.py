from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='employee_id',
            field=models.CharField(blank=True, help_text='Staff/Instructor ID within the school', max_length=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='organization.school'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('student', 'Student'), ('instructor', 'Instructor'), ('school_admin', 'School Admin'), ('admin', 'Admin')], default='student', max_length=20),
        ),
    ]
