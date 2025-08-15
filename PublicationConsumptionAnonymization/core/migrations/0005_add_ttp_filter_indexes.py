"""
Add database indexes for TTP filtering performance optimization
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_feed_created_by_feed_name_feed_status_and_more'),
    ]

    operations = [
        # Add indexes for common TTP filter fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_mitre_tactic ON ttp_data(mitre_tactic);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_mitre_tactic;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_mitre_technique_id ON ttp_data(mitre_technique_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_mitre_technique_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_created_at ON ttp_data(created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_updated_at ON ttp_data(updated_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_updated_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_threat_feed_id ON ttp_data(threat_feed_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_threat_feed_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_is_anonymized ON ttp_data(is_anonymized);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_is_anonymized;"
        ),
        
        # Add composite indexes for common filter combinations
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_tactic_created_at ON ttp_data(mitre_tactic, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_tactic_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_technique_created_at ON ttp_data(mitre_technique_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_technique_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_feed_created_at ON ttp_data(threat_feed_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_feed_created_at;"
        ),
        
        # Add partial indexes for non-null values
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_subtechnique_partial ON ttp_data(mitre_subtechnique) WHERE mitre_subtechnique IS NOT NULL AND mitre_subtechnique != '';",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_subtechnique_partial;"
        ),
        
        # Add basic text search indexes for name and description
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_name ON ttp_data(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_description ON ttp_data(description);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_description;"
        ),
        
        # Add indexes on threat feed fields for filtering
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_threat_feed_is_external ON core_threatfeed(is_external);",
            reverse_sql="DROP INDEX IF EXISTS idx_threat_feed_is_external;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_threat_feed_is_active ON core_threatfeed(is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_threat_feed_is_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_threat_feed_external_active ON core_threatfeed(is_external, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_threat_feed_external_active;"
        ),
    ]