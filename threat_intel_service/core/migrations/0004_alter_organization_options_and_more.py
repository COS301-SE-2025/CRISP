# Generated by Django 4.2.10 on 2025-05-27 12:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0003_feed_error_count_feed_last_bundle_id_feed_last_error_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='organization',
            name='contact_email',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='identity_class',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='sectors',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='stix_id',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='website',
        ),
        migrations.AddField(
            model_name='organization',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_organizations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
