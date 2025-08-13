# Generated migration for trust management integration with user management

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trust', '0001_initial_ut'),
        ('user_management', '0001_initial'),
    ]

    operations = [
        # Update TrustRelationship to use proper ForeignKey relationships
        migrations.AlterField(
            model_name='trustrelationship',
            name='source_organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='outgoing_trust_relationships',
                to='user_management.organization'
            ),
        ),
        migrations.AlterField(
            model_name='trustrelationship',
            name='target_organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='incoming_trust_relationships',
                to='user_management.organization'
            ),
        ),
        
        # Update TrustLog to use proper ForeignKey to CustomUser
        migrations.AlterField(
            model_name='trustlog',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='trust_logs_as_user',
                to='user_management.customuser'
            ),
        ),
        
        # TrustGroup created_by is already a CharField for organization ID, no change needed
        # Update TrustGroupMembership to reference the new organization model
        migrations.AlterField(
            model_name='trustgroupmembership',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='trust_group_memberships',
                to='user_management.organization'
            ),
        ),
        
        # Convert user approval fields from CharField to ForeignKey
        migrations.AlterField(
            model_name='trustrelationship',
            name='approved_by_source_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='trust_approvals_as_source',
                to='user_management.customuser',
                help_text="User who approved on behalf of source organization"
            ),
        ),
        migrations.AlterField(
            model_name='trustrelationship',
            name='approved_by_target_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='trust_approvals_as_target',
                to='user_management.customuser',
                help_text="User who approved on behalf of target organization"
            ),
        ),
        
        # Update TrustRelationship created_by to use proper ForeignKey
        migrations.AlterField(
            model_name='trustrelationship',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_trust_relationships',
                to='user_management.customuser',
                help_text="User who created this trust relationship"
            ),
        ),
        
        # Convert audit fields from CharField to ForeignKey  
        migrations.AlterField(
            model_name='trustrelationship',
            name='last_modified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='modified_trust_relationships',
                to='user_management.customuser',
                help_text="User who last modified this relationship"
            ),
        ),
        migrations.AddField(
            model_name='trustrelationship',
            name='revoked_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='revoked_trust_relationships',
                to='user_management.customuser',
                help_text="User who revoked this relationship"
            ),
        ),
        
        # Convert TrustLog fields from CharField to ForeignKey
        migrations.AlterField(
            model_name='trustlog',
            name='source_organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='trust_logs_as_source',
                to='user_management.organization',
                help_text="Organization that initiated the action"
            ),
        ),
        migrations.AlterField(
            model_name='trustlog',
            name='target_organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='trust_logs_as_target',
                to='user_management.organization',
                help_text="Target organization (if applicable)"
            ),
        ),
        migrations.AlterField(
            model_name='trustlog',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='trust_logs_as_user',
                to='user_management.customuser',
                help_text="User who performed the action"
            ),
        ),
        
        # Add missing metadata field to TrustLog
        migrations.AddField(
            model_name='trustlog',
            name='metadata',
            field=models.JSONField(
                default=dict,
                help_text="Additional metadata about the log entry"
            ),
        ),
    ]