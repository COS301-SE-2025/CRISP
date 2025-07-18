# Generated initial migration for CRISP Threat Intelligence Platform

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('identity_class', models.CharField(default='organization', max_length=100)),
                ('sectors', models.JSONField(blank=True, default=list, null=True)),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('stix_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_organizations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('alias', models.SlugField(unique=True)),
                ('can_read', models.BooleanField(default=True)),
                ('can_write', models.BooleanField(default=False)),
                ('media_types', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('default_anonymization', models.CharField(default='partial', max_length=50)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_collections', to='crisp_threat_intel.organization')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='STIXObject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('stix_id', models.CharField(max_length=255, unique=True)),
                ('stix_type', models.CharField(choices=[('indicator', 'Indicator'), ('malware', 'Malware'), ('attack-pattern', 'Attack Pattern'), ('threat-actor', 'Threat Actor'), ('identity', 'Identity'), ('relationship', 'Relationship'), ('tool', 'Tool'), ('vulnerability', 'Vulnerability'), ('observed-data', 'Observed Data'), ('report', 'Report'), ('course-of-action', 'Course of Action'), ('campaign', 'Campaign'), ('intrusion-set', 'Intrusion Set'), ('infrastructure', 'Infrastructure'), ('location', 'Location'), ('note', 'Note'), ('opinion', 'Opinion'), ('marking-definition', 'Marking Definition')], max_length=100)),
                ('spec_version', models.CharField(default='2.1', max_length=20)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
                ('created_by_ref', models.CharField(blank=True, max_length=255, null=True)),
                ('revoked', models.BooleanField(default=False)),
                ('labels', models.JSONField(default=list)),
                ('confidence', models.IntegerField(default=0)),
                ('external_references', models.JSONField(default=list)),
                ('object_marking_refs', models.JSONField(default=list)),
                ('granular_markings', models.JSONField(default=list)),
                ('raw_data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('anonymized', models.BooleanField(default=False)),
                ('anonymization_strategy', models.CharField(blank=True, max_length=50, null=True)),
                ('original_object_ref', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_stix_objects', to=settings.AUTH_USER_MODEL)),
                ('source_organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stix_objects', to='crisp_threat_intel.organization')),
            ],
        ),
        migrations.CreateModel(
            name='CollectionObject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_objects', to='crisp_threat_intel.collection')),
                ('stix_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_references', to='crisp_threat_intel.stixobject')),
            ],
        ),
        migrations.AddField(
            model_name='collection',
            name='stix_objects',
            field=models.ManyToManyField(related_name='collections', through='crisp_threat_intel.CollectionObject', to='crisp_threat_intel.stixobject'),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('query_parameters', models.JSONField(default=dict)),
                ('update_interval', models.IntegerField(default=3600)),
                ('status', models.CharField(choices=[('active', 'Active'), ('paused', 'Paused'), ('error', 'Error')], default='active', max_length=20)),
                ('last_published_time', models.DateTimeField(blank=True, null=True)),
                ('next_publish_time', models.DateTimeField(blank=True, null=True)),
                ('publish_count', models.IntegerField(default=0)),
                ('error_count', models.IntegerField(default=0)),
                ('last_bundle_id', models.CharField(blank=True, max_length=255, null=True)),
                ('last_error', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feeds', to='crisp_threat_intel.collection')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_feeds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Identity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stix_id', models.CharField(max_length=255, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('identity_class', models.CharField(max_length=100)),
                ('raw_data', models.TextField()),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stix_identity', to='crisp_threat_intel.organization')),
            ],
            options={
                'verbose_name_plural': 'Identities',
                'ordering': ['-modified'],
            },
        ),
        migrations.AddIndex(
            model_name='stixobject',
            index=models.Index(fields=['stix_type'], name='crisp_threa_stix_ty_7e6a86_idx'),
        ),
        migrations.AddIndex(
            model_name='stixobject',
            index=models.Index(fields=['created'], name='crisp_threa_created_bb39d1_idx'),
        ),
        migrations.AddIndex(
            model_name='stixobject',
            index=models.Index(fields=['modified'], name='crisp_threa_modifie_b0397b_idx'),
        ),
        migrations.AddIndex(
            model_name='stixobject',
            index=models.Index(fields=['created_by_ref'], name='crisp_threa_created_e79f50_idx'),
        ),
        migrations.AddIndex(
            model_name='stixobject',
            index=models.Index(fields=['anonymized'], name='crisp_threa_anonymi_0a2b6b_idx'),
        ),
        migrations.AddIndex(
            model_name='collectionobject',
            index=models.Index(fields=['collection', 'stix_object'], name='crisp_threa_collect_0b6e56_idx'),
        ),
        migrations.AddIndex(
            model_name='collectionobject',
            index=models.Index(fields=['date_added'], name='crisp_threa_date_ad_63f52a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='collectionobject',
            unique_together={('collection', 'stix_object')},
        ),
    ]