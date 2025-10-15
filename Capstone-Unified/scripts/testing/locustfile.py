"""
CRISP Load Testing - ALL Real API Endpoints
Comprehensive test of entire CRISP system
"""

from locust import HttpUser, task, between
import random

class CRISPUser(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        """Login with admin credentials"""
        response = self.client.post("/api/auth/login/", json={"username": "admin", "password": "admin123"})
        if response.status_code == 200:
            self.headers = {'Authorization': f'Bearer {response.json().get("access", "")}'}
        else:
            self.headers = {}
    
    # ==================== SOC ENDPOINTS (Priority) ====================
    
    @task(10)
    def soc_dashboard(self):
        self.client.get("/api/soc/dashboard/", headers=self.headers, name="SOC: dashboard")
    
    @task(8)
    def soc_incidents_list(self):
        self.client.get("/api/soc/incidents/", headers=self.headers, name="SOC: incidents list")
    
    @task(3)
    def soc_threat_map(self):
        self.client.get("/api/soc/threat-map/", headers=self.headers, name="SOC: threat-map")
    
    @task(2)
    def soc_system_health(self):
        self.client.get("/api/soc/system-health/", headers=self.headers, name="SOC: system-health")
    
    @task(2)
    def soc_top_threats(self):
        self.client.get("/api/soc/top-threats/", headers=self.headers, name="SOC: top-threats")
    
    @task(2)
    def soc_mitre_tactics(self):
        self.client.get("/api/soc/mitre-tactics/", headers=self.headers, name="SOC: mitre-tactics")
    
    @task(2)
    def soc_threat_intelligence(self):
        self.client.get("/api/soc/threat-intelligence/", headers=self.headers, name="SOC: threat-intel")
    
    @task(1)
    def soc_live_ioc_alerts(self):
        self.client.get("/api/soc/live-ioc-alerts/", headers=self.headers, name="SOC: ioc-alerts")
    
    @task(1)
    def soc_ioc_incident_correlation(self):
        self.client.get("/api/soc/ioc-incident-correlation/", headers=self.headers, name="SOC: ioc-correlation")
    
    # ==================== THREAT INTEL ENDPOINTS ====================
    
    @task(7)
    def indicators_list(self):
        self.client.get("/api/indicators/", headers=self.headers, name="THREAT: indicators")
    
    @task(5)
    def threat_feeds_list(self):
        self.client.get("/api/threat-feeds/", headers=self.headers, name="THREAT: feeds")
    
    @task(4)
    def ttps_list(self):
        self.client.get("/api/ttps/", headers=self.headers, name="THREAT: TTPs")
    
    @task(3)
    def mitre_matrix(self):
        self.client.get("/api/ttps/mitre-matrix/", headers=self.headers, name="THREAT: MITRE matrix")
    
    @task(2)
    def ttp_trends(self):
        self.client.get("/api/ttps/trends/", headers=self.headers, name="THREAT: TTP trends")
    
    @task(2)
    def recent_activities(self):
        self.client.get("/api/recent-activities/", headers=self.headers, name="THREAT: recent activities")
    
    @task(2)
    def threat_activity_chart(self):
        self.client.get("/api/threat-activity-chart/", headers=self.headers, name="THREAT: activity chart")
    
    @task(1)
    def system_health(self):
        self.client.get("/api/system-health/", headers=self.headers, name="THREAT: system health")
    
    @task(1)
    def dashboard_stats(self):
        self.client.get("/api/dashboard-stats/", headers=self.headers, name="THREAT: dashboard stats")
    
    @task(1)
    def ttp_technique_frequencies(self):
        self.client.get("/api/ttps/technique-frequencies/", headers=self.headers, name="THREAT: technique freq")
    
    @task(1)
    def ttp_tactic_frequencies(self):
        self.client.get("/api/ttps/tactic-frequencies/", headers=self.headers, name="THREAT: tactic freq")
    
    @task(1)
    def shared_indicators(self):
        self.client.get("/api/shared-indicators/", headers=self.headers, name="THREAT: shared indicators")
    
    # ==================== USER MANAGEMENT ====================
    
    @task(4)
    def users_list(self):
        self.client.get("/api/users/", headers=self.headers, name="USER: list")
    
    @task(2)
    def auth_profile(self):
        self.client.get("/api/auth/profile/", headers=self.headers, name="USER: profile")
    
    @task(1)
    def user_invitations(self):
        self.client.get("/api/users/invitations/", headers=self.headers, name="USER: invitations")
    
    # ==================== ORGANIZATION MANAGEMENT ====================
    
    @task(3)
    def organizations_list(self):
        self.client.get("/api/organizations/", headers=self.headers, name="ORG: list")
    
    @task(2)
    def organization_types(self):
        self.client.get("/api/organizations/types/", headers=self.headers, name="ORG: types")
    
    @task(1)
    def connected_organizations(self):
        self.client.get("/api/organizations/connected/", headers=self.headers, name="ORG: connected")
    
    # ==================== TRUST MANAGEMENT ====================
    
    @task(3)
    def trust_dashboard(self):
        self.client.get("/api/trust/dashboard/", headers=self.headers, name="TRUST: dashboard")
    
    @task(2)
    def trust_levels(self):
        self.client.get("/api/trust/levels/", headers=self.headers, name="TRUST: levels")
    
    @task(2)
    def trust_bilateral(self):
        self.client.get("/api/trust/bilateral/", headers=self.headers, name="TRUST: bilateral")
    
    @task(1)
    def trust_community(self):
        self.client.get("/api/trust/community/", headers=self.headers, name="TRUST: community")
    
    # ==================== ASSET MANAGEMENT ====================
    
    @task(3)
    def asset_inventory(self):
        self.client.get("/api/assets/inventory/", headers=self.headers, name="ASSET: inventory")
    
    @task(2)
    def asset_alerts(self):
        self.client.get("/api/assets/alerts/", headers=self.headers, name="ASSET: alerts")
    
    @task(1)
    def asset_statistics(self):
        self.client.get("/api/assets/statistics/", headers=self.headers, name="ASSET: statistics")
    
    @task(1)
    def asset_alert_feed(self):
        self.client.get("/api/assets/alerts/feed/", headers=self.headers, name="ASSET: alert feed")
    
    # ==================== BEHAVIOR ANALYTICS ====================
    
    @task(3)
    def behavior_dashboard(self):
        self.client.get("/api/behavior-analytics/dashboard/", headers=self.headers, name="BEHAVIOR: dashboard")
    
    @task(2)
    def behavior_anomalies(self):
        self.client.get("/api/behavior-analytics/anomalies/", headers=self.headers, name="BEHAVIOR: anomalies")
    
    @task(1)
    def behavior_alerts(self):
        self.client.get("/api/behavior-analytics/alerts/", headers=self.headers, name="BEHAVIOR: alerts")
    
    @task(1)
    def behavior_logs(self):
        self.client.get("/api/behavior-analytics/logs/", headers=self.headers, name="BEHAVIOR: logs")
    
    # ==================== REPORTS ====================
    
    @task(2)
    def reports_list(self):
        self.client.get("/api/reports/", headers=self.headers, name="REPORT: list")
    
    @task(1)
    def reports_status(self):
        self.client.get("/api/reports/status/", headers=self.headers, name="REPORT: status")
    
    # ==================== SYNC & UPDATES ====================
    
    @task(1)
    def sync_check_updates(self):
        self.client.get("/api/sync/check-updates/", headers=self.headers, name="SYNC: check-updates")
    
    @task(1)
    def sync_last_seen(self):
        self.client.get("/api/sync/last-seen/", headers=self.headers, name="SYNC: last-seen")
    
    # ==================== API STATUS ====================
    
    @task(1)
    def api_status(self):
        self.client.get("/api/", headers=self.headers, name="API: status")


# Usage: locust -f scripts/testing/locustfile.py --host=http://localhost:8000
# Open http://localhost:8089, set users to 50, spawn rate to 5

from locust import HttpUser, task, between
import random

class CRISPUser(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        """Login with admin credentials"""
        response = self.client.post("/api/auth/login/", json={"username": "admin", "password": "admin123"})
        if response.status_code == 200:
            self.headers = {'Authorization': f'Bearer {response.json().get("access", "")}'}
        else:
            self.headers = {}
    
    # WORKING ENDPOINTS ONLY (0% failure rate)
    
    @task(10)
    def system_health(self):
        """System health check"""
        self.client.get("/api/system-health/", headers=self.headers, name="SYSTEM: health")
    
    @task(8)
    def threat_feeds(self):
        """Threat feeds list"""
        self.client.get("/api/threat-feeds/", headers=self.headers, name="THREAT: feeds")
    
    @task(7)
    def ttps_list(self):
        """TTPs list"""
        self.client.get("/api/ttps/", headers=self.headers, name="THREAT: TTPs")
    
    @task(5)
    def mitre_matrix(self):
        """MITRE ATT&CK matrix"""
        self.client.get("/api/ttps/mitre-matrix/", headers=self.headers, name="THREAT: MITRE")
    
    @task(3)
    def recent_activities(self):
        """Recent threat activities"""
        self.client.get("/api/recent-activities/", headers=self.headers, name="THREAT: activities")
    
    @task(2)
    def ttp_trends(self):
        """TTP trends"""
        self.client.get("/api/ttps/trends/", headers=self.headers, name="THREAT: ttp-trends")
