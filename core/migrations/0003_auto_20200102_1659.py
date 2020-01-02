# Generated by Django 2.1.4 on 2020-01-02 16:59

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_20181217_0338_squashed_0003_killer_is_default'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='kill',
            unique_together={('writer', 'target', 'killer')},
        ),
    ]