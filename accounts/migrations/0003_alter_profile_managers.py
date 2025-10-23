import accounts.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile_role'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='profile',
            managers=[
                ('objects', accounts.managers.CustomUserManager()),
            ],
        ),
    ]
