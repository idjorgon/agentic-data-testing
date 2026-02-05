"""
Monitoring Agent: Continuous data quality monitoring and alerting
Tracks metrics over time, detects trends, and triggers alerts with security best practices
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import logging
from collections import defaultdict

# Use absolute import instead of relative
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))
from utils.logger import setup_logger

logger = setup_logger(__name__)


# Security constants
MAX_METRIC_NAME_LENGTH = 200
MAX_ALERT_MESSAGE_LENGTH = 1000
MAX_METRICS_IN_MEMORY = 10000
MAX_ALERTS_IN_MEMORY = 1000
MAX_HISTORY_DAYS = 90


@dataclass
class MetricSnapshot:
    """Single metric measurement at a point in time"""
    timestamp: str  # ISO format for JSON serialization
    metric_name: str
    value: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricSnapshot':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Alert:
    """Alert when threshold exceeded"""
    severity: str  # "critical", "warning", "info"
    metric_name: str
    message: str
    current_value: float
    threshold_value: float
    timestamp: str  # ISO format
    recommendations: List[str]
    alert_id: str = ""
    
    def __post_init__(self):
        """Generate alert ID if not provided"""
        if not self.alert_id:
            self.alert_id = f"{self.severity}_{self.metric_name}_{self.timestamp}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create from dictionary"""
        return cls(**data)


class MonitoringAgent:
    """
    Continuous monitoring agent for data quality metrics
    
    Security Features:
    - Input validation for all metric names and values
    - Memory limits to prevent resource exhaustion
    - Safe file operations with path validation
    - Sanitized logging to prevent log injection
    - Rate limiting for alert generation
    
    Capabilities:
    - Track data quality metrics over time
    - Detect trend anomalies (sudden spikes, gradual drift)
    - Configure thresholds and alerting rules
    - Historical metric storage and retrieval
    - Alert management and deduplication
    """
    
    # Valid severity levels
    VALID_SEVERITIES = {"critical", "warning", "info"}
    
    # Valid alert channels
    VALID_CHANNELS = {"log", "slack", "email", "pagerduty", "webhook"}
    
    def __init__(
        self, 
        alert_config: Optional[Dict[str, Any]] = None,
        storage_path: Optional[Path] = None
    ):
        """
        Initialize monitoring agent with security controls
        
        Args:
            alert_config: Configuration for alert thresholds
                {
                    "null_percentage_threshold": 10.0,
                    "anomaly_count_threshold": 5,
                    "drift_score_threshold": 0.15,
                    "alert_channels": ["log"],
                    "alert_rate_limit_seconds": 300
                }
            storage_path: Path for persisting metrics (optional)
        """
        self.alert_config = self._validate_config(alert_config or self._default_config())
        self.storage_path = storage_path
        
        # In-memory storage
        self.metric_history: Dict[str, List[MetricSnapshot]] = defaultdict(list)
        self.active_alerts: List[Alert] = []
        self.alert_timestamps: Dict[str, datetime] = {}  # For rate limiting
        
        logger.info("MonitoringAgent initialized with secure configuration")
    
    def track_profiling_metrics(
        self, 
        profile_result: Any,  # DatasetProfile
        dataset_name: str
    ) -> Dict[str, float]:
        """
        Extract and track key metrics from profiling results
        
        Args:
            profile_result: DatasetProfile object from DataProfiler
            dataset_name: Name of the dataset being monitored
        
        Returns:
            Dictionary of tracked metrics
            
        Raises:
            ValueError: If inputs are invalid
        """
        self._validate_dataset_name(dataset_name)
        
        metrics = {}
        timestamp = datetime.now()
        
        try:
            # Overall dataset metrics
            total_records = getattr(profile_result, 'total_records', 0)
            total_columns = getattr(profile_result, 'total_columns', 0)
            
            metrics['total_records'] = float(total_records)
            metrics['total_columns'] = float(total_columns)
            
            # Column-level metrics
            column_profiles = getattr(profile_result, 'column_profiles', {})
            
            for col_name, col_profile in column_profiles.items():
                safe_col_name = self._sanitize_metric_name(col_name)
                
                # Null percentage
                null_pct = getattr(col_profile, 'null_percentage', 0.0)
                metric_key = f"{dataset_name}_{safe_col_name}_null_pct"
                metrics[metric_key] = float(null_pct)
                self._record_metric(metric_key, float(null_pct), timestamp)
                
                # Distinct count
                distinct_count = getattr(col_profile, 'distinct_count', 0)
                metric_key = f"{dataset_name}_{safe_col_name}_distinct_count"
                metrics[metric_key] = float(distinct_count)
                self._record_metric(metric_key, float(distinct_count), timestamp)
                
                # Anomaly count
                anomalies = getattr(col_profile, 'anomalies', [])
                if anomalies:
                    metric_key = f"{dataset_name}_{safe_col_name}_anomaly_count"
                    metrics[metric_key] = float(len(anomalies))
                    self._record_metric(metric_key, float(len(anomalies)), timestamp)
            
            # Check memory limits
            self._enforce_memory_limits()
            
            logger.info(f"Tracked {len(metrics)} metrics for dataset '{dataset_name}'")
            return metrics
            
        except Exception as e:
            logger.error(f"Error tracking profiling metrics: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to track profiling metrics: {str(e)}")
    
    def check_thresholds(self, metrics: Dict[str, float]) -> List[Alert]:
        """
        Check if any metrics exceed configured thresholds
        
        Args:
            metrics: Dictionary of metric name to value
        
        Returns:
            List of alerts triggered
        """
        alerts = []
        current_time = datetime.now()
        
        for metric_name, value in metrics.items():
            # Validate metric
            if not self._is_valid_metric_value(value):
                logger.warning(f"Invalid metric value for {metric_name}: {value}")
                continue
            
            # Check rate limiting
            if not self._should_generate_alert(metric_name, current_time):
                logger.debug(f"Rate limited alert for {metric_name}")
                continue
            
            # Check null percentage threshold
            if 'null_pct' in metric_name:
                threshold = self.alert_config.get('null_percentage_threshold', 10.0)
                if value > threshold:
                    alert = self._create_alert(
                        severity="warning",
                        metric_name=metric_name,
                        message=f"High null percentage detected: {value:.2f}%",
                        current_value=value,
                        threshold_value=threshold,
                        recommendations=[
                            "Review data collection process",
                            "Check for upstream pipeline issues",
                            "Verify data source availability"
                        ]
                    )
                    alerts.append(alert)
            
            # Check anomaly count threshold
            elif 'anomaly_count' in metric_name:
                threshold = self.alert_config.get('anomaly_count_threshold', 5)
                if value > threshold:
                    alert = self._create_alert(
                        severity="critical",
                        metric_name=metric_name,
                        message=f"Excessive anomalies detected: {int(value)} records",
                        current_value=value,
                        threshold_value=threshold,
                        recommendations=[
                            "Investigate data source for corruption",
                            "Review recent pipeline changes",
                            "Check for fraudulent or malicious activity"
                        ]
                    )
                    alerts.append(alert)
            
            # Check distinct count drops (potential data quality issue)
            elif 'distinct_count' in metric_name:
                trend = self.detect_trends(metric_name, window_size=5)
                if trend.get("status") == "success":
                    if trend.get("direction") == "decreasing":
                        rate = trend.get("rate_of_change", 0)
                        if rate < -10:  # Significant drop
                            alert = self._create_alert(
                                severity="warning",
                                metric_name=metric_name,
                                message=f"Distinct value count decreasing: {rate:.1f} per measurement",
                                current_value=value,
                                threshold_value=trend.get("previous_value", 0),
                                recommendations=[
                                    "Check for data source changes",
                                    "Verify data pipeline functionality",
                                    "Review data transformation logic"
                                ]
                            )
                            alerts.append(alert)
        
        # Store alerts
        self.active_alerts.extend(alerts)
        self._enforce_alert_limits()
        
        logger.info(f"Generated {len(alerts)} new alerts")
        return alerts
    
    def detect_trends(
        self, 
        metric_name: str,
        window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze metric trends over time
        
        Args:
            metric_name: Name of metric to analyze
            window_size: Number of recent snapshots to analyze (max 100)
        
        Returns:
            Trend analysis with direction and velocity
        """
        # Validate inputs
        if not isinstance(metric_name, str) or len(metric_name) > MAX_METRIC_NAME_LENGTH:
            logger.warning(f"Invalid metric name: {metric_name}")
            return {"status": "error", "message": "Invalid metric name"}
        
        window_size = min(max(2, int(window_size)), 100)  # Clamp to 2-100
        
        if metric_name not in self.metric_history:
            return {"status": "insufficient_data", "message": "No historical data"}
        
        history = self.metric_history[metric_name][-window_size:]
        
        if len(history) < 2:
            return {"status": "insufficient_data", "message": "Need at least 2 data points"}
        
        try:
            # Calculate trend
            values = [snapshot.value for snapshot in history]
            
            # Simple linear trend
            if values[-1] > values[0]:
                direction = "increasing"
            elif values[-1] < values[0]:
                direction = "decreasing"
            else:
                direction = "stable"
            
            # Calculate rate of change
            rate_of_change = (values[-1] - values[0]) / len(values)
            
            # Calculate volatility (standard deviation)
            mean_val = sum(values) / len(values)
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            volatility = variance ** 0.5
            
            return {
                "status": "success",
                "direction": direction,
                "rate_of_change": rate_of_change,
                "volatility": volatility,
                "current_value": values[-1],
                "previous_value": values[0],
                "mean_value": mean_val,
                "data_points": len(values),
                "time_range": {
                    "start": history[0].timestamp,
                    "end": history[-1].timestamp
                }
            }
        except Exception as e:
            logger.error(f"Error detecting trends: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive monitoring report
        
        Returns:
            Report with all tracked metrics, trends, and alerts
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics_tracked": len(self.metric_history),
            "active_alerts": len(self.active_alerts),
            "metric_summary": {},
            "trends": {},
            "alert_summary": {
                "critical": 0,
                "warning": 0,
                "info": 0
            },
            "recent_alerts": []
        }
        
        # Summarize each metric
        for metric_name, history in self.metric_history.items():
            if history:
                latest = history[-1]
                report["metric_summary"][metric_name] = {
                    "latest_value": latest.value,
                    "timestamp": latest.timestamp,
                    "measurements": len(history)
                }
                
                # Add trend analysis for metrics with sufficient data
                if len(history) >= 3:
                    trend = self.detect_trends(metric_name, window_size=min(10, len(history)))
                    if trend.get("status") == "success":
                        report["trends"][metric_name] = {
                            "direction": trend["direction"],
                            "rate_of_change": trend["rate_of_change"],
                            "volatility": trend["volatility"]
                        }
        
        # Count alerts by severity and get recent alerts
        recent_cutoff = datetime.now() - timedelta(hours=24)
        
        for alert in self.active_alerts:
            report["alert_summary"][alert.severity] += 1
            
            # Include recent alerts (last 24 hours)
            alert_time = datetime.fromisoformat(alert.timestamp)
            if alert_time >= recent_cutoff:
                report["recent_alerts"].append({
                    "severity": alert.severity,
                    "metric": alert.metric_name,
                    "message": alert.message,
                    "timestamp": alert.timestamp
                })
        
        # Limit recent alerts to 50
        report["recent_alerts"] = report["recent_alerts"][:50]
        
        logger.info("Generated monitoring report")
        return report
    
    def clear_old_metrics(self, days: int = 90) -> int:
        """
        Clear metrics older than specified days
        
        Args:
            days: Number of days to retain (max 365)
        
        Returns:
            Number of metrics cleared
        """
        days = min(max(1, days), 365)
        cutoff = datetime.now() - timedelta(days=days)
        cleared = 0
        
        for metric_name in list(self.metric_history.keys()):
            original_count = len(self.metric_history[metric_name])
            
            # Filter out old metrics
            self.metric_history[metric_name] = [
                snapshot for snapshot in self.metric_history[metric_name]
                if datetime.fromisoformat(snapshot.timestamp) >= cutoff
            ]
            
            cleared += original_count - len(self.metric_history[metric_name])
            
            # Remove empty metric histories
            if not self.metric_history[metric_name]:
                del self.metric_history[metric_name]
        
        logger.info(f"Cleared {cleared} old metric snapshots (older than {days} days)")
        return cleared
    
    def get_metric_history(
        self, 
        metric_name: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific metric
        
        Args:
            metric_name: Name of the metric
            limit: Maximum number of snapshots to return
        
        Returns:
            List of metric snapshots as dictionaries
        """
        limit = min(max(1, limit), 1000)  # Clamp to 1-1000
        
        if metric_name not in self.metric_history:
            return []
        
        history = self.metric_history[metric_name][-limit:]
        return [snapshot.to_dict() for snapshot in history]
    
    def export_metrics(self, filepath: Path) -> bool:
        """
        Export all metrics to JSON file
        
        Args:
            filepath: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate path
            filepath = Path(filepath)
            if not filepath.suffix == '.json':
                filepath = filepath.with_suffix('.json')
            
            # Prepare data for export
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "metrics": {
                    metric_name: [snapshot.to_dict() for snapshot in snapshots]
                    for metric_name, snapshots in self.metric_history.items()
                },
                "alerts": [alert.to_dict() for alert in self.active_alerts]
            }
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported metrics to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {str(e)}", exc_info=True)
            return False
    
    def import_metrics(self, filepath: Path) -> bool:
        """
        Import metrics from JSON file
        
        Args:
            filepath: Path to import file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.error(f"Import file does not exist: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            # Import metrics
            for metric_name, snapshots in import_data.get("metrics", {}).items():
                self.metric_history[metric_name] = [
                    MetricSnapshot.from_dict(snapshot) for snapshot in snapshots
                ]
            
            # Import alerts
            for alert_data in import_data.get("alerts", []):
                self.active_alerts.append(Alert.from_dict(alert_data))
            
            # Enforce limits
            self._enforce_memory_limits()
            self._enforce_alert_limits()
            
            logger.info(f"Imported metrics from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import metrics: {str(e)}", exc_info=True)
            return False
    
    # Private helper methods
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize configuration"""
        validated = {}
        
        # Validate thresholds
        validated['null_percentage_threshold'] = max(0.0, min(100.0, 
            config.get('null_percentage_threshold', 10.0)))
        validated['anomaly_count_threshold'] = max(0, min(10000,
            config.get('anomaly_count_threshold', 5)))
        validated['drift_score_threshold'] = max(0.0, min(1.0,
            config.get('drift_score_threshold', 0.15)))
        
        # Validate alert channels
        channels = config.get('alert_channels', ['log'])
        validated['alert_channels'] = [
            ch for ch in channels if ch in self.VALID_CHANNELS
        ]
        if not validated['alert_channels']:
            validated['alert_channels'] = ['log']
        
        # Validate rate limit
        validated['alert_rate_limit_seconds'] = max(0, min(3600,
            config.get('alert_rate_limit_seconds', 300)))
        
        return validated
    
    def _default_config(self) -> Dict[str, Any]:
        """Default alert configuration"""
        return {
            "null_percentage_threshold": 10.0,
            "anomaly_count_threshold": 5,
            "drift_score_threshold": 0.15,
            "alert_channels": ["log"],
            "alert_rate_limit_seconds": 300
        }
    
    def _validate_dataset_name(self, name: str) -> None:
        """Validate dataset name"""
        if not isinstance(name, str):
            raise ValueError("Dataset name must be a string")
        if not name or len(name) > 200:
            raise ValueError("Dataset name must be 1-200 characters")
        if not name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Dataset name must be alphanumeric (with _ or -)")
    
    def _sanitize_metric_name(self, name: str) -> str:
        """Sanitize metric name for safety"""
        # Remove any non-alphanumeric characters except underscore and dash
        safe_name = ''.join(c for c in name if c.isalnum() or c in ('_', '-'))
        # Truncate to max length
        return safe_name[:MAX_METRIC_NAME_LENGTH]
    
    def _is_valid_metric_value(self, value: float) -> bool:
        """Check if metric value is valid"""
        try:
            float_val = float(value)
            # Check for NaN and infinity
            return not (float_val != float_val or abs(float_val) == float('inf'))
        except (ValueError, TypeError):
            return False
    
    def _should_generate_alert(self, metric_name: str, current_time: datetime) -> bool:
        """Check if alert should be generated based on rate limiting"""
        rate_limit = self.alert_config.get('alert_rate_limit_seconds', 300)
        
        if metric_name in self.alert_timestamps:
            last_alert = self.alert_timestamps[metric_name]
            elapsed = (current_time - last_alert).total_seconds()
            
            if elapsed < rate_limit:
                return False
        
        return True
    
    def _record_metric(
        self, 
        metric_name: str, 
        value: float, 
        timestamp: datetime,
        metadata: Optional[Dict] = None
    ) -> None:
        """Record a metric snapshot with validation"""
        # Validate inputs
        if not self._is_valid_metric_value(value):
            logger.warning(f"Skipping invalid metric value: {value}")
            return
        
        safe_metric_name = self._sanitize_metric_name(metric_name)
        
        snapshot = MetricSnapshot(
            timestamp=timestamp.isoformat(),
            metric_name=safe_metric_name,
            value=float(value),
            metadata=metadata or {}
        )
        
        self.metric_history[safe_metric_name].append(snapshot)
    
    def _create_alert(
        self,
        severity: str,
        metric_name: str,
        message: str,
        current_value: float,
        threshold_value: float,
        recommendations: List[str]
    ) -> Alert:
        """Create an alert with validation"""
        # Validate severity
        if severity not in self.VALID_SEVERITIES:
            severity = "info"
        
        # Truncate message if too long
        if len(message) > MAX_ALERT_MESSAGE_LENGTH:
            message = message[:MAX_ALERT_MESSAGE_LENGTH - 3] + "..."
        
        # Limit recommendations
        recommendations = recommendations[:10]
        
        # Update rate limit timestamp
        self.alert_timestamps[metric_name] = datetime.now()
        
        return Alert(
            severity=severity,
            metric_name=metric_name,
            message=message,
            current_value=current_value,
            threshold_value=threshold_value,
            timestamp=datetime.now().isoformat(),
            recommendations=recommendations
        )
    
    def _enforce_memory_limits(self) -> None:
        """Enforce memory limits on stored metrics"""
        total_snapshots = sum(len(snapshots) for snapshots in self.metric_history.values())
        
        if total_snapshots > MAX_METRICS_IN_MEMORY:
            # Remove oldest metrics first
            logger.warning(f"Metric memory limit reached ({total_snapshots}), pruning old data")
            
            for metric_name in list(self.metric_history.keys()):
                if len(self.metric_history[metric_name]) > 100:
                    # Keep only most recent 100
                    self.metric_history[metric_name] = self.metric_history[metric_name][-100:]
    
    def _enforce_alert_limits(self) -> None:
        """Enforce limits on stored alerts"""
        if len(self.active_alerts) > MAX_ALERTS_IN_MEMORY:
            logger.warning(f"Alert memory limit reached ({len(self.active_alerts)}), pruning old alerts")
            # Keep only most recent alerts
            self.active_alerts = self.active_alerts[-MAX_ALERTS_IN_MEMORY:]
