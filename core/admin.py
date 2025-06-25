from django.contrib import admin
from core.models.institution import Institution
from core.patterns.observer.threat_feed import ThreatFeed
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'created_at')
    search_fields = ('name', 'contact_email')

@admin.register(ThreatFeed)
class ThreatFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_external', 'is_public', 'last_sync')
    list_filter = ('is_external', 'is_public')
    search_fields = ('name', 'description')

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('type', 'value', 'threat_feed', 'confidence', 'created_at')
    list_filter = ('type', 'threat_feed', 'is_anonymized')
    search_fields = ('value', 'description')

@admin.register(TTPData)
class TTPDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'mitre_technique_id', 'mitre_tactic', 'threat_feed')
    list_filter = ('mitre_tactic', 'threat_feed', 'is_anonymized')
    search_fields = ('name', 'description', 'mitre_technique_id')
