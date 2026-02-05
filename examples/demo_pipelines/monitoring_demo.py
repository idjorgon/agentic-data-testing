"""
Demo: Continuous Monitoring with MonitoringAgent
Demonstrates real-time data quality monitoring and alerting WITHOUT using OpenAI API
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents import MonitoringAgent
from core import DataProfiler
from utils import load_json, setup_logger

# Setup logging
logger = setup_logger("monitoring_demo", level="INFO")


# Mock DatasetProfile class to simulate profiling results
class MockColumnProfile:
    """Mock column profile for demo"""
    def __init__(self, null_pct, distinct_count, anomalies=None):
        self.null_percentage = null_pct
        self.distinct_count = distinct_count
        self.anomalies = anomalies or []


class MockDatasetProfile:
    """Mock dataset profile for demo"""
    def __init__(self, total_records, total_columns, column_profiles):
        self.total_records = total_records
        self.total_columns = total_columns
        self.column_profiles = column_profiles


def simulate_daily_profiling(day: int, has_issues: bool = False):
    """
    Simulate a daily profiling result
    
    Args:
        day: Day number (for trend simulation)
        has_issues: Whether to inject data quality issues
    
    Returns:
        MockDatasetProfile with simulated metrics
    """
    base_records = 10000
    base_distinct = 500
    
    # Simulate gradual data changes over time
    records = base_records + (day * 100)
    
    # Build column profiles
    column_profiles = {}
    
    # Transaction ID column (should be stable)
    column_profiles['transaction_id'] = MockColumnProfile(
        null_pct=0.0,
        distinct_count=records  # Should match record count
    )
    
    # Amount column (may have anomalies)
    anomaly_count = 0
    if has_issues and day % 3 == 0:
        # Inject anomalies every 3 days if issues enabled
        anomaly_count = random.randint(5, 15)
    
    column_profiles['amount'] = MockColumnProfile(
        null_pct=0.1,
        distinct_count=int(records * 0.8),
        anomalies=[f"anomaly_{i}" for i in range(anomaly_count)]
    )
    
    # Status column (enum field)
    column_profiles['status'] = MockColumnProfile(
        null_pct=0.0,
        distinct_count=4  # approved, pending, rejected, flagged
    )
    
    # Optional fields with varying null percentages
    device_null_pct = 5.0 if not has_issues else min(5.0 + (day * 2), 80.0)
    column_profiles['device_id'] = MockColumnProfile(
        null_pct=device_null_pct,
        distinct_count=int(records * 0.3)
    )
    
    ip_null_pct = 8.0 if not has_issues else min(8.0 + (day * 2.5), 85.0)
    column_profiles['ip_address'] = MockColumnProfile(
        null_pct=ip_null_pct,
        distinct_count=int(records * 0.4)
    )
    
    # Merchant field
    merchant_distinct = max(100, base_distinct - (day * 10)) if has_issues else base_distinct
    column_profiles['merchant_id'] = MockColumnProfile(
        null_pct=0.5,
        distinct_count=merchant_distinct
    )
    
    return MockDatasetProfile(
        total_records=records,
        total_columns=len(column_profiles),
        column_profiles=column_profiles
    )


def run_monitoring_simulation():
    """
    Run a complete monitoring simulation over multiple days
    Shows normal operations transitioning to issues and recovery
    """
    print("=" * 80)
    print("📊 Continuous Data Quality Monitoring Simulation")
    print("=" * 80)
    print("\nThis demo simulates 14 days of data pipeline monitoring")
    print("WITHOUT using any OpenAI API calls - pure data quality tracking!\n")
    
    # Initialize monitoring agent with custom thresholds
    monitor = MonitoringAgent(alert_config={
        "null_percentage_threshold": 10.0,
        "anomaly_count_threshold": 5,
        "drift_score_threshold": 0.15,
        "alert_channels": ["log"],
        "alert_rate_limit_seconds": 60  # 1 minute for demo
    })
    
    print("✅ MonitoringAgent initialized with thresholds:")
    print(f"   • Null percentage: {monitor.alert_config['null_percentage_threshold']}%")
    print(f"   • Anomaly count: {monitor.alert_config['anomaly_count_threshold']}")
    print(f"   • Alert rate limit: {monitor.alert_config['alert_rate_limit_seconds']}s\n")
    
    # Simulate 14 days of monitoring
    print("🔄 Simulating 14 days of data pipeline monitoring...\n")
    print("-" * 80)
    
    all_alerts = []
    
    for day in range(1, 15):
        # Days 1-7: Normal operations
        # Days 8-11: Introduce data quality issues
        # Days 12-14: Recovery phase
        has_issues = 8 <= day <= 11
        
        # Simulate daily profiling
        profile = simulate_daily_profiling(day, has_issues=has_issues)
        
        # Track metrics
        dataset_name = "financial_transactions"
        metrics = monitor.track_profiling_metrics(profile, dataset_name)
        
        # Check for alerts
        alerts = monitor.check_thresholds(metrics)
        all_alerts.extend(alerts)
        
        # Display daily summary
        status_icon = "⚠️" if alerts else "✅"
        phase = "ISSUE PHASE" if has_issues else ("RECOVERY" if day > 11 else "NORMAL")
        
        print(f"{status_icon} Day {day:02d} ({phase}):")
        print(f"   Records: {profile.total_records:,}")
        print(f"   Metrics tracked: {len(metrics)}")
        
        if alerts:
            print(f"   🚨 Alerts triggered: {len(alerts)}")
            for alert in alerts:
                print(f"      • {alert.severity.upper()}: {alert.message}")
        else:
            print(f"   No alerts triggered")
        
        print()
    
    print("-" * 80)
    
    # Generate final report
    print("\n📋 Generating Comprehensive Monitoring Report...\n")
    report = monitor.generate_monitoring_report()
    
    print("=" * 80)
    print("📊 14-DAY MONITORING SUMMARY")
    print("=" * 80)
    print(f"\n📈 Overall Statistics:")
    print(f"   • Total metrics tracked: {report['metrics_tracked']}")
    print(f"   • Total active alerts: {report['active_alerts']}")
    print(f"   • Critical alerts: {report['alert_summary']['critical']}")
    print(f"   • Warning alerts: {report['alert_summary']['warning']}")
    print(f"   • Info alerts: {report['alert_summary']['info']}")
    
    # Show trend analysis
    print(f"\n📉 Trend Analysis:")
    if report['trends']:
        trend_count = 0
        for metric_name, trend in list(report['trends'].items())[:5]:
            trend_count += 1
            direction_icon = "📈" if trend['direction'] == "increasing" else "📉" if trend['direction'] == "decreasing" else "➡️"
            print(f"   {direction_icon} {metric_name}:")
            print(f"      Direction: {trend['direction']}")
            print(f"      Rate of change: {trend['rate_of_change']:.2f} per measurement")
            print(f"      Volatility: {trend['volatility']:.2f}")
        
        if len(report['trends']) > 5:
            print(f"   ... and {len(report['trends']) - 5} more metrics")
    else:
        print("   No trends detected (insufficient data)")
    
    # Show metric summary
    print(f"\n📊 Latest Metric Values:")
    for metric_name, summary in list(report['metric_summary'].items())[:8]:
        print(f"   • {metric_name}: {summary['latest_value']:.2f}")
    
    if len(report['metric_summary']) > 8:
        print(f"   ... and {len(report['metric_summary']) - 8} more metrics")
    
    # Alert breakdown
    print(f"\n🚨 Alert Breakdown by Phase:")
    print(f"   • Normal Phase (Days 1-7): Minimal alerts expected")
    print(f"   • Issue Phase (Days 8-11): High alerts due to data quality degradation")
    print(f"   • Recovery Phase (Days 12-14): Alerts should decrease")
    
    # Show some example alerts
    if all_alerts:
        print(f"\n⚠️ Example Alerts (first 5):")
        for i, alert in enumerate(all_alerts[:5], 1):
            print(f"\n   Alert {i}:")
            print(f"   Severity: {alert.severity.upper()}")
            print(f"   Metric: {alert.metric_name}")
            print(f"   Message: {alert.message}")
            print(f"   Recommendations:")
            for rec in alert.recommendations[:2]:
                print(f"      • {rec}")
    
    print("\n" + "=" * 80)
    print("✨ Monitoring Simulation Complete!")
    print("=" * 80)
    print("\n💡 Key Takeaways:")
    print("   1. MonitoringAgent tracks metrics over time WITHOUT API calls")
    print("   2. Automatic threshold-based alerting catches issues early")
    print("   3. Trend analysis identifies gradual degradation")
    print("   4. Rate limiting prevents alert fatigue")
    print("   5. Actionable recommendations guide remediation")
    print("\n🎯 Production-Ready Features:")
    print("   • Security: Input validation, memory limits, sanitization")
    print("   • Scalability: Efficient in-memory storage with pruning")
    print("   • Reliability: Error handling and graceful degradation")
    print("   • Observability: Comprehensive logging and reporting")


def run_interactive_monitoring():
    """
    Interactive demo allowing user to trigger different scenarios
    """
    print("=" * 80)
    print("🎮 Interactive Monitoring Demo")
    print("=" * 80)
    print("\nChoose a scenario to simulate:\n")
    print("1. Normal data pipeline (no issues)")
    print("2. High null percentage issue")
    print("3. Anomaly spike (potential fraud/corruption)")
    print("4. Distinct value drop (data source problem)")
    print("5. Run full 14-day simulation")
    print("6. Exit")
    
    monitor = MonitoringAgent()
    
    while True:
        try:
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == "6":
                print("\n👋 Goodbye!")
                break
            
            if choice == "5":
                run_monitoring_simulation()
                continue
            
            # Single scenario simulations
            if choice in ["1", "2", "3", "4"]:
                dataset_name = "test_dataset"
                
                if choice == "1":
                    print("\n✅ Simulating: Normal pipeline...")
                    profile = MockDatasetProfile(
                        total_records=10000,
                        total_columns=5,
                        column_profiles={
                            'id': MockColumnProfile(0.0, 10000),
                            'amount': MockColumnProfile(0.1, 8000),
                            'status': MockColumnProfile(0.0, 4),
                        }
                    )
                
                elif choice == "2":
                    print("\n⚠️ Simulating: High null percentage...")
                    profile = MockDatasetProfile(
                        total_records=10000,
                        total_columns=5,
                        column_profiles={
                            'id': MockColumnProfile(0.0, 10000),
                            'device_id': MockColumnProfile(85.0, 1500),  # High nulls!
                            'user_email': MockColumnProfile(72.0, 3000),  # High nulls!
                        }
                    )
                
                elif choice == "3":
                    print("\n🚨 Simulating: Anomaly spike...")
                    profile = MockDatasetProfile(
                        total_records=10000,
                        total_columns=5,
                        column_profiles={
                            'amount': MockColumnProfile(
                                0.1, 8000,
                                anomalies=[f"anomaly_{i}" for i in range(25)]  # 25 anomalies!
                            ),
                        }
                    )
                
                elif choice == "4":
                    print("\n📉 Simulating: Distinct value drop...")
                    # Need history for trend detection
                    for day in range(1, 6):
                        distinct_count = 500 - (day * 50)  # Gradual drop
                        profile = MockDatasetProfile(
                            total_records=10000,
                            total_columns=5,
                            column_profiles={
                                'merchant_id': MockColumnProfile(0.5, distinct_count),
                            }
                        )
                        monitor.track_profiling_metrics(profile, dataset_name)
                    
                    print(f"   Tracked 5 days of declining distinct values")
                
                # Track and alert
                metrics = monitor.track_profiling_metrics(profile, dataset_name)
                alerts = monitor.check_thresholds(metrics)
                
                print(f"\n📊 Results:")
                print(f"   Metrics tracked: {len(metrics)}")
                print(f"   Alerts triggered: {len(alerts)}")
                
                if alerts:
                    print(f"\n⚠️ Alerts:")
                    for alert in alerts:
                        print(f"\n   {alert.severity.upper()}: {alert.message}")
                        print(f"   Current: {alert.current_value:.2f}, Threshold: {alert.threshold_value:.2f}")
                        print(f"   Recommendations:")
                        for rec in alert.recommendations:
                            print(f"      • {rec}")
                else:
                    print(f"\n✅ No alerts - all metrics within thresholds")
            
            else:
                print("Invalid choice. Please enter 1-6.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Monitoring Agent Demo - No OpenAI API required!"
    )
    parser.add_argument(
        "--mode",
        choices=["simulation", "interactive"],
        default="simulation",
        help="Demo mode: simulation (14-day auto) or interactive (choose scenarios)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "interactive":
            run_interactive_monitoring()
        else:
            run_monitoring_simulation()
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
        sys.exit(1)
