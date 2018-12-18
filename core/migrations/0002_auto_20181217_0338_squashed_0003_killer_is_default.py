# Generated by Django 2.1 on 2018-12-18 02:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('core', '0002_auto_20181217_0338'), ('core', '0003_killer_is_default')]

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kill',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='assigned', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='kill',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='targetting', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='kill',
            name='writer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='written', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='killer',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
