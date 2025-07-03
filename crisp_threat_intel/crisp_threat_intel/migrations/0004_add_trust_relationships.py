# Generated migration for TrustRelationship model and integrated anonymization

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crisp_threat_intel', '0003_alter_collection_stix_objects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrustRelationship',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('trust_level', models.FloatField(default=0.5, help_text='Trust level between 0.0 (no trust) and 1.0 (full trust)')),
                ('anonymization_strategy', models.CharField(default='integrated', help_text='Anonymization strategy to use for this relationship', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_trust_relationships', to=settings.AUTH_USER_MODEL)),
                ('source_organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_trust_relationships', to='crisp_threat_intel.organization')),
                ('target_organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_trust_relationships', to='crisp_threat_intel.organization')),
            ],
        ),
        migrations.AddIndex(
            model_name='trustrelationship',
            index=models.Index(fields=['source_organization', 'target_organization'], name='crisp_threa_source__82f8e6_idx'),
        ),
        migrations.AddIndex(
            model_name='trustrelationship',
            index=models.Index(fields=['trust_level'], name='crisp_threa_trust_l_5d41a9_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='trustrelationship',
            unique_together={('source_organization', 'target_organization')},
        ),
    ]