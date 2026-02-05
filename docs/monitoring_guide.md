# Monitoring Agent Guide

## Overview

The **MonitoringAgent** provides continuous data quality monitoring and alerting capabilities without requiring any OpenAI API calls. It's designed with enterprise-grade security and best practices for production data pipeline monitoring.

## Key Features

✅ **Pure Python Analytics** - No external API dependencies for core functionality  
🔒 **Security Hardened** - Input validation, memory limits, sanitization  
📊 **Metric Tracking** - Track data quality metrics over time  
⚠️ **Smart Alerting** - Threshold-based alerts with rate limiting  
📈 **Trend Detection** - Identify gradual degradation or sudden spikes  
💾 **Export/Import** - Persist metrics for long-term analysis  
🎯 **Production-Ready** - Comprehensive error handling and logging  

---

## Quick Start

### Basic Usage

```python
from agents import MonitoringAgent
from core import DataProfiler
from utils import load_json

# Initialize monitoring agent
monitor = MonitoringAgent(alert_config={
    "null_percentage_threshold": 10.0,
    "anomaly_count_threshold": 5,
    "alert_channels": ["log"]
})

# Profile your dataset
profiler = DataProfiler()
data = load_json("data/transactions.json")
profile = profiler.profile_dataset(data, "transactions")

# Track metrics
metrics = monitor.track_profiling_metrics(profile, "transactions")

# Check for alerts
alerts = monitor.check_thresholds(metrics)

if alerts:
    print(f"⚠️ {len(alerts)} alerts triggered!")
    for alert in alerts:
        print(f"{alert.severity}: {alert.message}")
```

---

## Configuration

### Alert Configuration

```python
alert_config = {
    # Threshold for null percentage alerts (%)
    "null_percentage_threshold": 10.0,
    
    # Threshold for anomaly count alerts
    "anomaly_count_threshold": 5,
    
    # Threshold for drift score alerts
    "drift_score_threshold": 0.15,
    
    # Alert channels (log, slack, email, pagerduty, webhook)
    "alert_channels": ["log", "slack"],
    
    # Rate limit in seconds (prevents alert spam)
    "alert_rate_limit_seconds": 300  # 5 minutes
}

monitor = MonitoringAgent(alert_config=alert_config)
```

### Storage Configuration

```python
from pathlib import Path

# Enable persistent storage
monitor = MonitoringAgent(
    alert_config=config,
    storage_path=Path("./monitoring_data")
)
```

---

## Core Capabilities

### 1. Metric Tracking

Track data quality metrics extracted from profiling results:

```python
# After profiling a dataset
profile = profiler.profile_dataset(data, "financial_transactions")

# Track all relevant metrics
metrics = monitor.track_profiling_metrics(profile, "financial_transactions")

# Returns dictionary like:
{
    "financial_transactions_amount_null_pct": 5.2,
    "financial_transactions_amount_distinct_count": 8543,
    "financial_transactions_amount_anomaly_count": 3,
    "financial_transactions_status_null_pct": 0.0,
    ...
}
```

**Automatically tracked metrics:**
- Null percentages per column
- Distinct value counts per column
- Anomaly counts per column
- Total record count
- Total column count

### 2. Threshold Checking

Automatically checks metrics against configured thresholds:

```python
alerts = monitor.check_thresholds(metrics)

for alert in alerts:
    print(f"Severity: {alert.severity}")  # "critical", "warning", "info"
    print(f"Metric: {alert.metric_name}")
    print(f"Message: {alert.message}")
    print(f"Current Value: {alert.current_value}")
    print(f"Threshold: {alert.threshold_value}")
    print(f"Recommendations:")
    for rec in alert.recommendations:
        print(f"  • {rec}")
```

**Alert Types:**

1. **Null Percentage Alert** (Warning)
   - Triggered when null % exceeds threshold
   - Recommendations: Check data collection, verify upstream pipelines

2. **Anomaly Count Alert** (Critical)
   - Triggered when anomaly count exceeds threshold
   - Recommendations: Investigate corruption, check for fraud

3. **Distinct Value Drop Alert** (Warning)
   - Triggered when distinct count trends downward significantly
   - Recommendations: Review data source changes, verify transformations

### 3. Trend Detection

Analyze how metrics change over time:

```python
# Analyze trend for a specific metric
trend = monitor.detect_trends(
    "financial_transactions_amount_null_pct",
    window_size=10  # Last 10 measurements
)

if trend['status'] == "success":
    print(f"Direction: {trend['direction']}")  # "increasing", "decreasing", "stable"
    print(f"Rate of change: {trend['rate_of_change']}")
    print(f"Volatility: {trend['volatility']}")
    print(f"Current value: {trend['current_value']}")
    print(f"Previous value: {trend['previous_value']}")
```

**Trend Analysis Provides:**
- **Direction**: Overall trend direction
- **Rate of Change**: Average change per measurement
- **Volatility**: Standard deviation (stability indicator)
- **Time Range**: Start and end timestamps

### 4. Monitoring Reports

Generate comprehensive monitoring reports:

```python
report = monitor.generate_monitoring_report()

print(f"Metrics tracked: {report['metrics_tracked']}")
print(f"Active alerts: {report['active_alerts']}")
print(f"Critical: {report['alert_summary']['critical']}")
print(f"Warnings: {report['alert_summary']['warning']}")

# Access metric summaries
for metric, summary in report['metric_summary'].items():
    print(f"{metric}: {summary['latest_value']}")

# Review trends
for metric, trend in report['trends'].items():
    print(f"{metric} is {trend['direction']}")
```

**Report Contents:**
- Total metrics tracked
- Active alert count
- Alert summary by severity
- Latest values for all metrics
- Trend analysis for metrics with sufficient history
- Recent alerts (last 24 hours)

### 5. Data Persistence

Export and import metrics for long-term storage:

```python
# Export to JSON
monitor.export_metrics(Path("monitoring_history.json"))

# Import from JSON (e.g., on restart)
monitor.import_metrics(Path("monitoring_history.json"))
```

**Use Cases:**
- Persist metrics across application restarts
- Share monitoring data between teams
- Integrate with external dashboarding tools
- Historical analysis and reporting

### 6. Metric History Queries

Retrieve historical data for specific metrics:

```python
# Get last 100 snapshots for a metric
history = monitor.get_metric_history(
    "financial_transactions_amount_null_pct",
    limit=100
)

for snapshot in history[-5:]:  # Last 5
    print(f"{snapshot['timestamp']}: {snapshot['value']}")
```

### 7. Cleanup Operations

Manage memory usage by clearing old data:

```python
# Clear metrics older than 30 days
cleared_count = monitor.clear_old_metrics(days=30)
print(f"Cleared {cleared_count} old metric snapshots")
```

---

## Integration with Orchestrator

The MonitoringAgent is integrated into the OrchestratorAgent for seamless workflow:

```python
from agents import OrchestratorAgent
from core import DataProfiler
from utils import load_json

orchestrator = OrchestratorAgent()
profiler = DataProfiler()

# Load data
data = load_json("data/transactions.json")

# Profile
profile = profiler.profile_dataset(data, "transactions")

# Track and monitor via orchestrator
result = orchestrator.track_and_monitor(profile, "transactions")

if result['status'] == 'success':
    print(f"Metrics tracked: {result['metrics_tracked']}")
    print(f"Alerts triggered: {result['alerts_triggered']}")
    
    for alert in result['alerts']:
        print(f"{alert['severity']}: {alert['message']}")

# Get comprehensive monitoring report
report = orchestrator.get_monitoring_report()
```

---

## Production Deployment

### Daily Monitoring Workflow

```python
import schedule
import time
from agents import MonitoringAgent
from core import DataProfiler
from utils import load_json

# Initialize once
profiler = DataProfiler()
monitor = MonitoringAgent(alert_config={
    "null_percentage_threshold": 10.0,
    "anomaly_count_threshold": 5,
    "alert_channels": ["slack", "email"]
})

def daily_monitoring_job():
    """Run daily data quality checks"""
    # Load today's data
    data = load_json("data/daily/latest.json")
    
    # Profile
    profile = profiler.profile_dataset(data, "transactions")
    
    # Track metrics
    metrics = monitor.track_profiling_metrics(profile, "transactions")
    
    # Check for issues
    alerts = monitor.check_thresholds(metrics)
    
    if alerts:
        # Alerts automatically sent to configured channels
        print(f"⚠️ {len(alerts)} issues detected!")
    
    # Export daily snapshot
    monitor.export_metrics(f"metrics/daily_{date.today()}.json")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(daily_monitoring_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Alerting Best Practices

1. **Configure Appropriate Thresholds**
   - Start conservative, tune based on baseline
   - Different thresholds for different datasets
   - Consider business impact when setting levels

2. **Use Rate Limiting**
   - Prevent alert fatigue
   - Default: 300 seconds (5 minutes)
   - Adjust based on your team's response capacity

3. **Prioritize Critical Alerts**
   - Anomaly spikes = Critical
   - Null percentage = Warning
   - Use severity levels effectively

4. **Provide Context**
   - Alerts include current vs threshold values
   - Actionable recommendations included
   - Link to runbooks in production

5. **Monitor the Monitors**
   - Track alert frequency
   - Review false positive rates
   - Adjust thresholds quarterly

### Security Considerations

The MonitoringAgent implements multiple security layers:

#### Input Validation
```python
# Metric names are sanitized
# Valid: "transactions_amount_null_pct"
# Invalid characters removed: "transactions<script>alert</script>"
# Result: "transactionsscriptalertscript"

# Metric values validated
# NaN, Infinity rejected
# Only valid float values accepted
```

#### Memory Limits
```python
# Prevents resource exhaustion attacks
MAX_METRICS_IN_MEMORY = 10000  # Total snapshots across all metrics
MAX_ALERTS_IN_MEMORY = 1000    # Maximum stored alerts
MAX_HISTORY_DAYS = 90          # Default retention period
```

#### Safe File Operations
```python
# Path validation when exporting/importing
# Only .json files allowed
# Absolute path resolution
# No path traversal attacks possible
```

#### Sanitized Logging
```python
# No injection attacks via metric names
# Control characters stripped
# Safe for log aggregation systems
```

---

## Advanced Features

### Custom Alert Channels

Extend the MonitoringAgent to support custom alert channels:

```python
class CustomMonitoringAgent(MonitoringAgent):
    def _send_to_custom_channel(self, alert):
        """Send to your custom alerting system"""
        # Implement your integration
        custom_api.send_alert({
            "severity": alert.severity,
            "message": alert.message,
            "recommendations": alert.recommendations
        })
```

### Metric Aggregation

Aggregate metrics for dashboarding:

```python
def aggregate_daily_metrics(monitor, metric_name, days=7):
    """Aggregate last N days of metrics"""
    history = monitor.get_metric_history(metric_name, limit=days)
    
    values = [h['value'] for h in history]
    
    return {
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
        "count": len(values)
    }

# Example usage
agg = aggregate_daily_metrics(monitor, "transactions_amount_null_pct", days=7)
print(f"Last 7 days - Min: {agg['min']}, Max: {agg['max']}, Avg: {agg['avg']}")
```

### Integration with External Tools

#### Export to Prometheus

```python
def export_to_prometheus_format(monitor):
    """Export metrics in Prometheus format"""
    report = monitor.generate_monitoring_report()
    
    metrics = []
    for name, summary in report['metric_summary'].items():
        metrics.append(f"{name} {summary['latest_value']}")
    
    return "\n".join(metrics)
```

#### Export to DataDog

```python
from datadog import statsd

def send_to_datadog(monitor):
    """Send metrics to DataDog"""
    report = monitor.generate_monitoring_report()
    
    for name, summary in report['metric_summary'].items():
        statsd.gauge(f"data_quality.{name}", summary['latest_value'])
```

---

## Troubleshooting

### Issue: No Alerts Generated

**Check:**
1. Are thresholds too high?
2. Is rate limiting preventing alerts?
3. Are metrics being tracked correctly?

```python
# Debug metric tracking
metrics = monitor.track_profiling_metrics(profile, "dataset")
print(f"Tracked metrics: {list(metrics.keys())}")
print(f"Values: {metrics}")

# Check thresholds
print(f"Config: {monitor.alert_config}")
```

### Issue: Too Many Alerts

**Solutions:**
1. Increase thresholds
2. Increase rate limit window
3. Review data quality at source

```python
# Adjust configuration
monitor.alert_config['null_percentage_threshold'] = 15.0
monitor.alert_config['alert_rate_limit_seconds'] = 600  # 10 minutes
```

### Issue: Memory Usage High

**Solutions:**
1. Clear old metrics regularly
2. Reduce retention period
3. Export and clear periodically

```python
# Regular cleanup
monitor.clear_old_metrics(days=30)

# Export before clearing
monitor.export_metrics("backup.json")
```

---

## API Reference

### MonitoringAgent Class

#### `__init__(alert_config, storage_path)`
Initialize monitoring agent with configuration.

#### `track_profiling_metrics(profile_result, dataset_name)`
Extract and track metrics from profiling results.

#### `check_thresholds(metrics)`
Check metrics against configured thresholds, return alerts.

#### `detect_trends(metric_name, window_size)`
Analyze metric trends over specified window.

#### `generate_monitoring_report()`
Generate comprehensive monitoring report.

#### `export_metrics(filepath)`
Export all metrics to JSON file.

#### `import_metrics(filepath)`
Import metrics from JSON file.

#### `get_metric_history(metric_name, limit)`
Retrieve historical snapshots for metric.

#### `clear_old_metrics(days)`
Remove metrics older than specified days.

### Alert Class

**Properties:**
- `severity`: "critical", "warning", or "info"
- `metric_name`: Name of the metric that triggered alert
- `message`: Human-readable alert message
- `current_value`: Current metric value
- `threshold_value`: Configured threshold
- `timestamp`: ISO format timestamp
- `recommendations`: List of actionable recommendations
- `alert_id`: Unique alert identifier

### MetricSnapshot Class

**Properties:**
- `timestamp`: ISO format timestamp
- `metric_name`: Name of the metric
- `value`: Metric value (float)
- `metadata`: Additional context (dict)

---

## Examples

See `examples/demo_pipelines/monitoring_demo.py` for a complete working example with:
- 14-day monitoring simulation
- Interactive scenario testing
- Normal operations vs issues vs recovery phases
- Comprehensive reporting

Run it:
```bash
python examples/demo_pipelines/monitoring_demo.py --mode simulation
```

---

## Best Practices Summary

1. ✅ **Start Simple**: Begin with basic thresholds, refine over time
2. ✅ **Monitor Continuously**: Schedule regular checks (daily/hourly)
3. ✅ **Act on Alerts**: Have runbooks for common alert types
4. ✅ **Export Regularly**: Persist metrics for long-term analysis
5. ✅ **Review Trends**: Weekly trend review prevents issues
6. ✅ **Clean Up**: Regular cleanup prevents memory bloat
7. ✅ **Test Alerts**: Simulate failures to verify alerting works
8. ✅ **Document Thresholds**: Keep threshold rationale documented
9. ✅ **Integrate Early**: Add monitoring from day one
10. ✅ **Iterate**: Continuously improve based on feedback

---

## Support

For issues or questions:
- Review the demo: `examples/demo_pipelines/monitoring_demo.py`
- Check logs for detailed error messages
- See main README.md for architecture overview
