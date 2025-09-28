"""
User Behavior Analytics Service
Implements algorithms for detecting suspicious user activities and behavioral anomalies
"""

import logging
import statistics
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from django.contrib.auth import get_user_model
from django.core.cache import cache

# Optional enhanced analytics dependencies
try:
    import numpy as np
    import pandas as pd
    from scipy import stats
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    ENHANCED_ANALYTICS_AVAILABLE = True
except ImportError:
    ENHANCED_ANALYTICS_AVAILABLE = False
from core.models.user_behavior_models import (
    UserBehaviorBaseline, UserSession, BehaviorAnomaly, 
    UserActivityLog, BehaviorAlert
)

User = get_user_model()
logger = logging.getLogger(__name__)


class UserBehaviorAnalyticsService:
    """
    Service for analyzing user behavior patterns and detecting anomalies
    """
    
    def __init__(self):
        self.baseline_period_days = 30  # Days to use for baseline calculation
        self.anomaly_threshold_multiplier = 2.5  # Standard deviations for anomaly detection
        self.confidence_threshold = 70  # Minimum confidence score for alerts
        self.enhanced_analytics = ENHANCED_ANALYTICS_AVAILABLE
        
        if self.enhanced_analytics:
            logger.info("Enhanced analytics (numpy, pandas, sklearn) available")
        else:
            logger.info("Using basic analytics (Python stdlib only)")
        
    def create_user_baseline(self, user: User) -> UserBehaviorBaseline:
        """
        Create or update behavioral baseline for a user
        """
        logger.info(f"Creating baseline for user {user.username}")
        
        # Calculate baseline period
        end_date = timezone.now()
        start_date = end_date - timedelta(days=self.baseline_period_days)
        
        # Get user sessions for baseline period
        sessions = UserSession.objects.filter(
            user=user,
            start_time__gte=start_date,
            start_time__lte=end_date,
            end_time__isnull=False  # Only completed sessions
        )
        
        if sessions.count() < 5:  # Need minimum sessions for reliable baseline
            logger.warning(f"Insufficient session data for {user.username} baseline")
            return None
            
        baseline, created = UserBehaviorBaseline.objects.get_or_create(
            user=user,
            defaults={
                'baseline_period_start': start_date,
                'baseline_period_end': end_date,
            }
        )
        
        # Calculate login patterns
        baseline.avg_login_frequency_per_day = self._calculate_login_frequency(sessions)
        baseline.avg_session_duration_minutes = self._calculate_avg_session_duration(sessions)
        baseline.common_login_hours = self._calculate_common_login_hours(sessions)
        baseline.common_login_days = self._calculate_common_login_days(sessions)
        
        # Calculate activity patterns
        baseline.avg_api_calls_per_session = self._calculate_avg_api_calls(sessions)
        baseline.common_accessed_endpoints = self._calculate_common_endpoints(sessions)
        baseline.avg_data_access_volume = self._calculate_avg_data_access(sessions)
        
        # Calculate geographical patterns
        baseline.common_ip_ranges = self._calculate_common_ip_ranges(sessions)
        baseline.common_user_agents = self._calculate_common_user_agents(sessions)
        
        # Calculate SOC-specific patterns
        baseline.avg_incidents_created_per_week = self._calculate_incident_creation_rate(user, start_date, end_date)
        baseline.avg_incidents_assigned_per_week = self._calculate_incident_assignment_rate(user, start_date, end_date)
        baseline.common_incident_categories = self._calculate_common_incident_categories(user, start_date, end_date)
        
        # Update metadata
        baseline.baseline_period_start = start_date
        baseline.baseline_period_end = end_date
        baseline.total_sessions_analyzed = sessions.count()
        baseline.save()
        
        logger.info(f"Baseline created/updated for {user.username} with {sessions.count()} sessions")
        return baseline
    
    def analyze_session_for_anomalies(self, session: UserSession) -> List[BehaviorAnomaly]:
        """
        Analyze a user session for behavioral anomalies
        """
        anomalies = []
        user = session.user
        
        try:
            baseline = UserBehaviorBaseline.objects.get(user=user)
        except UserBehaviorBaseline.DoesNotExist:
            logger.warning(f"No baseline found for {user.username}, creating one")
            baseline = self.create_user_baseline(user)
            if not baseline:
                return anomalies
        
        # Check login frequency anomaly
        anomalies.extend(self._detect_login_frequency_anomaly(session, baseline))
        
        # Check login time anomaly
        anomalies.extend(self._detect_login_time_anomaly(session, baseline))
        
        # Check session duration anomaly
        anomalies.extend(self._detect_session_duration_anomaly(session, baseline))
        
        # Check API usage anomaly
        anomalies.extend(self._detect_api_usage_anomaly(session, baseline))
        
        # Check data access anomaly
        anomalies.extend(self._detect_data_access_anomaly(session, baseline))
        
        # Check geographical anomaly
        anomalies.extend(self._detect_geographical_anomaly(session, baseline))
        
        # Check concurrent sessions
        anomalies.extend(self._detect_concurrent_sessions_anomaly(session))
        
        # Check incident manipulation patterns
        anomalies.extend(self._detect_incident_manipulation_anomaly(session, baseline))
        
        # Update session anomaly status
        if anomalies:
            session.is_anomalous = True
            session.anomaly_score = max([a.confidence_score for a in anomalies])
            session.anomaly_reasons = [a.anomaly_type for a in anomalies]
            session.save()
            
            # Create alerts for high-confidence anomalies
            self._create_behavior_alerts(anomalies)
        
        return anomalies
    
    def _detect_login_frequency_anomaly(self, session: UserSession, baseline: UserBehaviorBaseline) -> List[BehaviorAnomaly]:
        """
        Detect unusual login frequency patterns
        """
        anomalies = []
        user = session.user
        
        # Check logins in the last 24 hours
        recent_sessions = UserSession.objects.filter(
            user=user,
            start_time__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        expected_daily_logins = baseline.avg_login_frequency_per_day
        threshold = expected_daily_logins * self.anomaly_threshold_multiplier
        
        if recent_sessions > threshold and expected_daily_logins > 0:
            deviation = ((recent_sessions - expected_daily_logins) / expected_daily_logins) * 100
            confidence = min(95, max(50, deviation))
            
            anomaly = BehaviorAnomaly.objects.create(
                user=user,
                session=session,
                anomaly_type='login_frequency',
                severity=self._calculate_severity(confidence),
                confidence_score=confidence,
                title=f"Unusual login frequency detected for {user.username}",
                description=f"User logged in {recent_sessions} times in 24h, baseline is {expected_daily_logins:.1f}",
                detection_method="Statistical threshold analysis",
                baseline_value=expected_daily_logins,
                observed_value=recent_sessions,
                deviation_percentage=deviation,
                context_data={
                    'time_window': '24 hours',
                    'threshold_multiplier': self.anomaly_threshold_multiplier
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _detect_login_time_anomaly(self, session: UserSession, baseline: UserBehaviorBaseline) -> List[BehaviorAnomaly]:
        """
        Detect logins at unusual times
        """
        anomalies = []
        
        login_hour = session.start_time.hour
        login_day = session.start_time.weekday()  # 0=Monday, 6=Sunday
        
        common_hours = baseline.common_login_hours
        common_days = baseline.common_login_days
        
        # Check if login time is outside common patterns
        hour_anomaly = common_hours and login_hour not in common_hours
        day_anomaly = common_days and login_day not in common_days
        
        if hour_anomaly or day_anomaly:
            confidence = 60 if hour_anomaly and day_anomaly else 45
            
            # Increase confidence for very unusual times (e.g., 2-5 AM)
            if login_hour in [2, 3, 4, 5] and hour_anomaly:
                confidence += 20
            
            anomaly = BehaviorAnomaly.objects.create(
                user=session.user,
                session=session,
                anomaly_type='login_time',
                severity=self._calculate_severity(confidence),
                confidence_score=confidence,
                title=f"Unusual login time for {session.user.username}",
                description=f"Login at {session.start_time.strftime('%H:%M on %A')} is outside normal pattern",
                detection_method="Time pattern analysis",
                context_data={
                    'login_hour': login_hour,
                    'login_day': login_day,
                    'common_hours': common_hours,
                    'common_days': common_days,
                    'hour_anomaly': hour_anomaly,
                    'day_anomaly': day_anomaly
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _detect_session_duration_anomaly(self, session: UserSession, baseline: UserBehaviorBaseline) -> List[BehaviorAnomaly]:
        """
        Detect unusually long or short sessions
        """
        anomalies = []
        
        if not session.duration_minutes or not baseline.avg_session_duration_minutes:
            return anomalies
        
        expected_duration = baseline.avg_session_duration_minutes
        actual_duration = session.duration_minutes
        
        # Check for sessions that are unusually long or short
        deviation_threshold = expected_duration * 3  # 3x normal duration
        
        if actual_duration > deviation_threshold or actual_duration < (expected_duration * 0.1):
            deviation = ((actual_duration - expected_duration) / expected_duration) * 100
            confidence = min(90, max(50, abs(deviation) / 2))
            
            anomaly_type = "unusually_long" if actual_duration > deviation_threshold else "unusually_short"
            
            anomaly = BehaviorAnomaly.objects.create(
                user=session.user,
                session=session,
                anomaly_type='session_duration',
                severity=self._calculate_severity(confidence),
                confidence_score=confidence,
                title=f"Unusual session duration for {session.user.username}",
                description=f"Session lasted {actual_duration:.1f} minutes, baseline is {expected_duration:.1f} minutes",
                detection_method="Duration threshold analysis",
                baseline_value=expected_duration,
                observed_value=actual_duration,
                deviation_percentage=deviation,
                context_data={
                    'anomaly_subtype': anomaly_type,
                    'threshold_multiplier': 3
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _detect_api_usage_anomaly(self, session: UserSession, baseline: UserBehaviorBaseline) -> List[BehaviorAnomaly]:
        """
        Detect unusual API usage patterns
        """
        anomalies = []
        
        if not baseline.avg_api_calls_per_session:
            return anomalies
        
        expected_api_calls = baseline.avg_api_calls_per_session
        actual_api_calls = session.api_calls_count
        threshold = expected_api_calls * 5  # 5x normal usage
        
        if actual_api_calls > threshold:
            deviation = ((actual_api_calls - expected_api_calls) / expected_api_calls) * 100
            confidence = min(95, max(60, deviation / 5))
            
            anomaly = BehaviorAnomaly.objects.create(
                user=session.user,
                session=session,
                anomaly_type='api_usage',
                severity=self._calculate_severity(confidence),
                confidence_score=confidence,
                title=f"Unusual API usage for {session.user.username}",
                description=f"Made {actual_api_calls} API calls, baseline is {expected_api_calls:.1f}",
                detection_method="API usage threshold analysis",
                baseline_value=expected_api_calls,
                observed_value=actual_api_calls,
                deviation_percentage=deviation,
                context_data={
                    'threshold_multiplier': 5,
                    'endpoints_accessed': session.endpoints_accessed
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _detect_data_access_anomaly(self, session: UserSession, baseline: UserBehaviorBaseline) -> List[BehaviorAnomaly]:
        """
        Detect unusual data access volumes
        """
        anomalies = []
        
        if not baseline.avg_data_access_volume:
            return anomalies
        
        expected_volume = baseline.avg_data_access_volume
        actual_volume = session.data_records_accessed
        threshold = expected_volume * 10  # 10x normal access
        
        if actual_volume > threshold:
            deviation = ((actual_volume - expected_volume) / expected_volume) * 100
            confidence = min(95, max(70, deviation / 10))
            
            severity = 'critical' if actual_volume > threshold * 2 else self._calculate_severity(confidence)
            
            anomaly = BehaviorAnomaly.objects.create(
                user=session.user,
                session=session,
                anomaly_type='data_access',
                severity=severity,
                confidence_score=confidence,
                title=f"Potential data exfiltration by {session.user.username}",
                description=f"Accessed {actual_volume} records, baseline is {expected_volume:.1f}",
                detection_method="Data volume threshold analysis",
                baseline_value=expected_volume,
                observed_value=actual_volume,
                deviation_percentage=deviation,
                context_data={
                    'threshold_multiplier': 10,
                    'exports_performed': session.exports_performed
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _detect_geographical_anomaly(self, session: UserSession, baseline: UserBehaviorBaseline) -> List[BehaviorAnomaly]:
        """
        Detect logins from unusual locations
        """
        anomalies = []
        
        current_ip = session.ip_address
        common_ip_ranges = baseline.common_ip_ranges
        
        # Simple IP range matching (could be enhanced with GeoIP)
        is_known_ip = any(current_ip.startswith(ip_range) for ip_range in common_ip_ranges)
        
        if not is_known_ip and common_ip_ranges:
            confidence = 65
            
            # Check if it's a private IP (less suspicious)
            if current_ip.startswith(('10.', '192.168.', '172.')):
                confidence = 45
            
            anomaly = BehaviorAnomaly.objects.create(
                user=session.user,
                session=session,
                anomaly_type='login_location',
                severity=self._calculate_severity(confidence),
                confidence_score=confidence,
                title=f"Login from unusual location for {session.user.username}",
                description=f"Login from IP {current_ip} not in common patterns",
                detection_method="IP range pattern analysis",
                context_data={
                    'current_ip': current_ip,
                    'common_ip_ranges': common_ip_ranges,
                    'is_private_ip': current_ip.startswith(('10.', '192.168.', '172.'))
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _detect_concurrent_sessions_anomaly(self, session: UserSession) -> List[BehaviorAnomaly]:
        """
        Detect unusual concurrent sessions
        """
        anomalies = []
        
        # Count active sessions for this user
        active_sessions = UserSession.objects.filter(
            user=session.user,
            start_time__lte=session.start_time,
            end_time__isnull=True  # Still active
        ).exclude(id=session.id).count()
        
        if active_sessions > 2:  # More than 2 concurrent sessions
            confidence = min(85, 50 + (active_sessions * 10))
            
            anomaly = BehaviorAnomaly.objects.create(
                user=session.user,
                session=session,
                anomaly_type='concurrent_sessions',
                severity=self._calculate_severity(confidence),
                confidence_score=confidence,
                title=f"Multiple concurrent sessions for {session.user.username}",
                description=f"User has {active_sessions + 1} active sessions simultaneously",
                detection_method="Concurrent session count analysis",
                observed_value=active_sessions + 1,
                context_data={
                    'concurrent_session_count': active_sessions + 1,
                    'threshold': 2
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _detect_incident_manipulation_anomaly(self, session: UserSession, baseline: UserBehaviorBaseline) -> List[BehaviorAnomaly]:
        """
        Detect unusual incident creation/modification patterns
        """
        anomalies = []
        
        total_incident_activity = (session.incidents_created + 
                                  session.incidents_modified + 
                                  session.incidents_assigned)
        
        # Check for rapid incident creation/modification
        if total_incident_activity > 10:  # More than 10 incident actions in one session
            confidence = min(90, 60 + (total_incident_activity * 2))
            
            anomaly = BehaviorAnomaly.objects.create(
                user=session.user,
                session=session,
                anomaly_type='incident_manipulation',
                severity=self._calculate_severity(confidence),
                confidence_score=confidence,
                title=f"Unusual incident activity by {session.user.username}",
                description=f"Performed {total_incident_activity} incident actions in single session",
                detection_method="Incident activity threshold analysis",
                observed_value=total_incident_activity,
                context_data={
                    'incidents_created': session.incidents_created,
                    'incidents_modified': session.incidents_modified,
                    'incidents_assigned': session.incidents_assigned,
                    'threshold': 10
                }
            )
            anomalies.append(anomaly)
            
        return anomalies
    
    def _create_behavior_alerts(self, anomalies: List[BehaviorAnomaly]):
        """
        Create real-time alerts for high-confidence anomalies
        """
        for anomaly in anomalies:
            if anomaly.confidence_score >= self.confidence_threshold:
                alert_type = self._determine_alert_type(anomaly)
                
                BehaviorAlert.objects.create(
                    user=anomaly.user,
                    anomaly=anomaly,
                    alert_type=alert_type,
                    priority=anomaly.severity,
                    title=f"Behavior Alert: {anomaly.title}",
                    message=anomaly.description,
                    recommended_actions=self._get_recommended_actions(anomaly)
                )
                
                logger.warning(f"Behavior alert created: {anomaly.title}")
    
    def _determine_alert_type(self, anomaly: BehaviorAnomaly) -> str:
        """
        Determine the appropriate alert type based on anomaly characteristics
        """
        if anomaly.anomaly_type in ['data_access', 'bulk_export']:
            return 'data_exfiltration'
        elif anomaly.anomaly_type in ['privilege_escalation', 'incident_manipulation']:
            return 'immediate'
        elif anomaly.confidence_score >= 80:
            return 'suspicious'
        else:
            return 'policy_violation'
    
    def _get_recommended_actions(self, anomaly: BehaviorAnomaly) -> List[str]:
        """
        Get recommended actions based on anomaly type
        """
        actions = []
        
        if anomaly.anomaly_type == 'login_frequency':
            actions = [
                "Verify user identity through additional authentication",
                "Check for compromised credentials",
                "Review recent password changes"
            ]
        elif anomaly.anomaly_type == 'data_access':
            actions = [
                "Immediately review data access logs",
                "Consider temporary access restriction",
                "Investigate potential data exfiltration",
                "Contact user to verify legitimate business need"
            ]
        elif anomaly.anomaly_type == 'login_location':
            actions = [
                "Verify user's current location",
                "Check for VPN or proxy usage",
                "Consider requiring additional authentication"
            ]
        else:
            actions = [
                "Investigate user activity patterns",
                "Contact user to verify legitimate activity",
                "Monitor continued behavior"
            ]
            
        return actions
    
    # Helper methods for baseline calculations
    def _calculate_login_frequency(self, sessions) -> float:
        """Calculate average daily login frequency"""
        if not sessions.exists():
            return 0.0
        
        session_dates = sessions.values_list('start_time__date', flat=True)
        unique_dates = len(set(session_dates))
        total_sessions = sessions.count()
        
        return total_sessions / max(unique_dates, 1)
    
    def _calculate_avg_session_duration(self, sessions) -> float:
        """Calculate average session duration in minutes"""
        durations = sessions.filter(duration_minutes__isnull=False).values_list('duration_minutes', flat=True)
        return statistics.mean(durations) if durations else 0.0
    
    def _calculate_common_login_hours(self, sessions) -> List[int]:
        """Calculate most common login hours"""
        hours = [session.start_time.hour for session in sessions]
        hour_counts = Counter(hours)
        # Return hours that appear in more than 20% of sessions
        threshold = len(hours) * 0.2
        return [hour for hour, count in hour_counts.items() if count >= threshold]
    
    def _calculate_common_login_days(self, sessions) -> List[int]:
        """Calculate most common login days"""
        days = [session.start_time.weekday() for session in sessions]
        day_counts = Counter(days)
        # Return days that appear in more than 15% of sessions
        threshold = len(days) * 0.15
        return [day for day, count in day_counts.items() if count >= threshold]
    
    def _calculate_avg_api_calls(self, sessions) -> float:
        """Calculate average API calls per session"""
        api_calls = sessions.values_list('api_calls_count', flat=True)
        return statistics.mean(api_calls) if api_calls else 0.0
    
    def _calculate_common_endpoints(self, sessions) -> List[str]:
        """Calculate most commonly accessed endpoints"""
        all_endpoints = []
        for session in sessions:
            all_endpoints.extend(session.endpoints_accessed)
        
        endpoint_counts = Counter(all_endpoints)
        # Return top 10 most common endpoints
        return [endpoint for endpoint, count in endpoint_counts.most_common(10)]
    
    def _calculate_avg_data_access(self, sessions) -> float:
        """Calculate average data records accessed per session"""
        data_access = sessions.values_list('data_records_accessed', flat=True)
        return statistics.mean(data_access) if data_access else 0.0
    
    def _calculate_common_ip_ranges(self, sessions) -> List[str]:
        """Calculate common IP address ranges"""
        ips = sessions.values_list('ip_address', flat=True)
        ip_prefixes = set()
        
        for ip in ips:
            # Extract /24 subnet (first 3 octets)
            parts = ip.split('.')
            if len(parts) >= 3:
                prefix = f"{parts[0]}.{parts[1]}.{parts[2]}"
                ip_prefixes.add(prefix)
        
        return list(ip_prefixes)
    
    def _calculate_common_user_agents(self, sessions) -> List[str]:
        """Calculate most common user agents"""
        user_agents = sessions.values_list('user_agent', flat=True)
        agent_counts = Counter(user_agents)
        # Return top 5 most common user agents
        return [agent for agent, count in agent_counts.most_common(5)]
    
    def _calculate_incident_creation_rate(self, user: User, start_date: datetime, end_date: datetime) -> float:
        """Calculate average incidents created per week"""
        from soc.models import SOCIncident
        
        incidents = SOCIncident.objects.filter(
            created_by=user,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        weeks = (end_date - start_date).days / 7
        return incidents / max(weeks, 1)
    
    def _calculate_incident_assignment_rate(self, user: User, start_date: datetime, end_date: datetime) -> float:
        """Calculate average incidents assigned per week"""
        from soc.models import SOCIncident
        
        incidents = SOCIncident.objects.filter(
            assigned_to=user,
            assigned_at__gte=start_date,
            assigned_at__lte=end_date
        ).count()
        
        weeks = (end_date - start_date).days / 7
        return incidents / max(weeks, 1)
    
    def _calculate_common_incident_categories(self, user: User, start_date: datetime, end_date: datetime) -> List[str]:
        """Calculate most common incident categories for user"""
        from soc.models import SOCIncident
        
        categories = SOCIncident.objects.filter(
            created_by=user,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values_list('category', flat=True)
        
        category_counts = Counter(categories)
        return [cat for cat, count in category_counts.most_common(5)]
    
    def _calculate_severity(self, confidence_score: float) -> str:
        """Calculate severity based on confidence score"""
        if confidence_score >= 85:
            return 'critical'
        elif confidence_score >= 70:
            return 'high'
        elif confidence_score >= 50:
            return 'medium'
        else:
            return 'low'
    
    def get_user_behavior_summary(self, user: User, days: int = 7) -> Dict:
        """
        Get a summary of user behavior for the specified period
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        sessions = UserSession.objects.filter(
            user=user,
            start_time__gte=start_date
        )
        
        anomalies = BehaviorAnomaly.objects.filter(
            user=user,
            detected_at__gte=start_date
        )
        
        alerts = BehaviorAlert.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        return {
            'user': user.username,
            'period_days': days,
            'total_sessions': sessions.count(),
            'anomalous_sessions': sessions.filter(is_anomalous=True).count(),
            'total_anomalies': anomalies.count(),
            'critical_anomalies': anomalies.filter(severity='critical').count(),
            'active_alerts': alerts.filter(is_acknowledged=False).count(),
            'avg_session_duration': sessions.aggregate(
                avg_duration=Avg('duration_minutes')
            )['avg_duration'] or 0,
            'unique_ip_addresses': sessions.values('ip_address').distinct().count(),
            'anomaly_types': list(
                anomalies.values('anomaly_type').annotate(
                    count=Count('anomaly_type')
                ).values_list('anomaly_type', 'count')
            )
        }
    
    def enhanced_anomaly_detection(self, user: User, days: int = 7) -> List[Dict]:
        """
        Enhanced anomaly detection using machine learning (when available)
        """
        if not self.enhanced_analytics:
            logger.warning("Enhanced analytics not available, falling back to basic detection")
            return []
        
        try:
            # Get user activity data
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            activities = UserActivityLog.objects.filter(
                user=user,
                timestamp__gte=start_date
            ).values(
                'timestamp', 'action_type', 'response_status', 'duration_ms'
            )
            
            if len(activities) < 10:  # Need minimum data for ML
                return []
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(list(activities))
            
            # Feature engineering
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['is_success'] = (df['response_status'] < 400).astype(int)
            
            # Create feature matrix
            features = df[['hour', 'day_of_week', 'duration_ms', 'is_success']].fillna(0)
            
            # Normalize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Isolation Forest for anomaly detection
            isolation_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_scores = isolation_forest.fit_predict(features_scaled)
            
            # Get anomaly indices
            anomaly_indices = np.where(anomaly_scores == -1)[0]
            
            anomalies = []
            for idx in anomaly_indices:
                activity = activities[idx]
                confidence = abs(isolation_forest.score_samples([features_scaled[idx]])[0]) * 100
                
                anomalies.append({
                    'timestamp': activity['timestamp'],
                    'anomaly_type': 'ml_detected',
                    'confidence_score': min(95, max(60, confidence)),
                    'description': f"ML-detected anomalous activity pattern",
                    'activity_details': activity
                })
            
            logger.info(f"Enhanced ML detection found {len(anomalies)} anomalies for {user.username}")
            return anomalies
            
        except Exception as e:
            logger.error(f"Enhanced anomaly detection failed: {e}")
            return []
    
    def get_analytics_capabilities(self) -> Dict:
        """
        Return information about available analytics capabilities
        """
        capabilities = {
            'basic_statistics': True,
            'threshold_detection': True,
            'baseline_learning': True,
            'enhanced_ml': self.enhanced_analytics
        }
        
        if self.enhanced_analytics:
            capabilities.update({
                'isolation_forest': True,
                'statistical_tests': True,
                'pandas_processing': True,
                'numpy_computations': True
            })
        
        return capabilities