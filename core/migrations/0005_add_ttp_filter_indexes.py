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
            "CREATE INDEX IF NOT EXISTS idx_ttp_mitre_tactic ON core_ttpdata(mitre_tactic);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_mitre_tactic;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_mitre_technique_id ON core_ttpdata(mitre_technique_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_mitre_technique_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_created_at ON core_ttpdata(created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_updated_at ON core_ttpdata(updated_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_updated_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_threat_feed_id ON core_ttpdata(threat_feed_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_threat_feed_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_is_anonymized ON core_ttpdata(is_anonymized);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_is_anonymized;"
        ),
        
        # Add composite indexes for common filter combinations
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_tactic_created_at ON core_ttpdata(mitre_tactic, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_tactic_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_technique_created_at ON core_ttpdata(mitre_technique_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_technique_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_feed_created_at ON core_ttpdata(threat_feed_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_feed_created_at;"
        ),
        
        # Add partial indexes for non-null values
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_subtechnique_partial ON core_ttpdata(mitre_subtechnique) WHERE mitre_subtechnique IS NOT NULL AND mitre_subtechnique != '';",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_subtechnique_partial;"
        ),
        
        # Add full-text search indexes for name and description
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_name_trgm ON core_ttpdata USING gin(name gin_trgm_ops);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_name_trgm;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_ttp_description_trgm ON core_ttpdata USING gin(description gin_trgm_ops);",
            reverse_sql="DROP INDEX IF EXISTS idx_ttp_description_trgm;"
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