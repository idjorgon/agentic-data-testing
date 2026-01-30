# Data Profiling Implementation Guide

## Overview

Data profiling has been added to catch data quality issues, drift, and anomalies **before they become production incidents**.

## What Was Implemented

### 1. DataProfiler Class (`src/core/data_profiler.py`)

**Core Features:**
- **Column Profiling**: Type inference, null counts, distinct values, distributions
- **Statistical Analysis**: Min/max, mean, median, standard deviation for numeric columns
- **Anomaly Detection**: IQR and Z-score methods for outlier identification
- **Drift Detection**: Compare baseline vs current data to detect schema/distribution changes
- **Categorical Analysis**: Top values and frequency distributions

### 2. Integration with Financial Demo

The [`financial_validation_demo.py`](examples/demo_pipelines/financial_validation_demo.py) now includes:

**STEP 1: Data Profiling**
- Profile all columns in the dataset
- Display statistics for each column
- Detect anomalies in transaction amounts
- Check for data drift
- Save baseline profile for future comparisons

**STEP 2: Validation** (existing workflow)
- Execute test workflow
- Generate reports

## Usage Examples

### Basic Profiling

```python
from core import DataProfiler

# Initialize profiler
profiler = DataProfiler(drift_threshold=0.1)

# Profile your dataset
profile = profiler.profile_dataset(
    data=transactions,
    dataset_name="financial_transactions"
)

# Access results
print(f"Total records: {profile.total_records}")
print(f"Total columns: {profile.total_columns}")

# Check individual columns
for column_name, column_profile in profile.column_profiles.items():
    print(f"{column_name}: {column_profile.data_type}")
    print(f"  Nulls: {column_profile.null_percentage:.1f}%")
    print(f"  Distinct: {column_profile.distinct_count}")
    
    if column_profile.anomalies:
        for anomaly in column_profile.anomalies:
            print(f"  ⚠️  {anomaly}")
```

### Anomaly Detection

```python
# Find outliers in transaction amounts
anomalies = profiler.find_anomalies(
    data=transactions,
    column="amount",
    method="iqr"  # or "zscore"
)

# Review anomalies
for anomaly in anomalies:
    print(f"Record #{anomaly['record_index']}")
    print(f"  Value: ${anomaly['anomaly_value']:.2f}")
    print(f"  Reason: {anomaly['reason']}")
    print(f"  Score: {anomaly['anomaly_score']:.2f}")
```

### Drift Detection

```python
from utils import load_json, save_json

# Create baseline (first run)
baseline_profile = profiler.profile_dataset(yesterday_data)
save_json(baseline_profile.to_dict(), "baseline_profile.json")

# Check for drift (subsequent runs)
drift_results = profiler.detect_drift(baseline_profile, today_data)

for column, drift_result in drift_results.items():
    if drift_result.has_drift:
        print(f"⚠️  DRIFT in '{column}':")
        print(f"   Score: {drift_result.drift_score:.2f}")
        for detail in drift_result.drift_details:
            print(f"   - {detail}")
```

### Save & Load Profiles

```python
from utils import save_json, load_json

# Save profile for baseline
save_json(profile.to_dict(), "baseline_profile.json")

# Load and compare later
baseline_dict = load_json("baseline_profile.json")

# Reconstruct DatasetProfile
from core import DatasetProfile, ProfileResult

baseline_profile = DatasetProfile(
    total_records=baseline_dict["total_records"],
    total_columns=baseline_dict["total_columns"],
    column_profiles={
        name: ProfileResult(**col_dict)
        for name, col_dict in baseline_dict["column_profiles"].items()
    },
    profile_timestamp=baseline_dict["profile_timestamp"],
    dataset_name=baseline_dict.get("dataset_name")
)
```

## Key Metrics Tracked

### For All Columns:
- Data type (integer, float, string, boolean, datetime)
- Null count & percentage
- Distinct values count & percentage
- Top values (for categorical data)

### For Numeric Columns:
- Min / Max values
- Mean / Median
- Standard deviation
- Outlier detection (IQR or Z-score)

### For String Columns:
- Min / Max / Mean length
- Pattern analysis
- Top values

## Anomaly Detection Methods

### IQR (Interquartile Range) - Default
- Good for skewed distributions
- Flags values outside Q1 - 1.5×IQR to Q3 + 1.5×IQR
- More robust to outliers

```python
anomalies = profiler.find_anomalies(data, "amount", method="iqr")
```

### Z-Score
- Good for normal distributions
- Flags values with |z-score| > 3
- Sensitive to extreme outliers

```python
anomalies = profiler.find_anomalies(data, "amount", method="zscore")
```

## Drift Detection Thresholds

Configure drift sensitivity:

```python
profiler = DataProfiler(drift_threshold=0.1)  # 10% threshold
```

Drift is detected when:
- Null percentage changes > threshold × 100%
- Distinct count changes > threshold × 100%
- Value distribution shifts > threshold
- Mean changes > threshold × 100% (for numeric)

## Production Use Cases

### 1. Pre-Pipeline Validation
```python
# Before running expensive transformations
profile = profiler.profile_dataset(input_data)

for column, col_profile in profile.column_profiles.items():
    if col_profile.null_percentage > 50:
        raise ValueError(f"Too many nulls in {column}!")
```

### 2. Daily Data Quality Monitoring
```python
# Compare today vs yesterday
drift = profiler.detect_drift(yesterday_profile, today_data)

if any(d.has_drift for d in drift.values()):
    send_alert("Data drift detected!")
```

### 3. Anomaly Alerting
```python
# Flag suspicious transactions
anomalies = profiler.find_anomalies(transactions, "amount", method="iqr")

if anomalies:
    for anomaly in anomalies[:10]:  # Top 10
        if anomaly["anomaly_score"] > threshold:
            flag_for_review(anomaly["record"])
```

## Running the Demo

```bash
# Activate virtual environment
source venv/bin/activate

# Run financial validation with profiling
python examples/demo_pipelines/financial_validation_demo.py
```

The demo will:
1. Profile the financial transactions dataset
2. Display key statistics for each column
3. Detect anomalies in transaction amounts
4. Check for data drift
5. Save baseline profile to `reports/baseline_profile.json`
6. Continue with validation workflow
7. Generate comprehensive reports

## Next Steps

Consider adding:
1. **Real-time Monitoring**: Integrate with Airflow/dbt to run on every pipeline execution
2. **Alert Integration**: Send Slack/email when anomalies or drift detected
3. **Historical Trending**: Track data quality metrics over time
4. **Custom Rules**: Add domain-specific profiling logic
5. **ML-based Detection**: Use isolation forests or autoencoders for advanced anomaly detection

## Files Modified/Created

- ✅ `src/core/data_profiler.py` - Main profiling engine (NEW)
- ✅ `src/core/__init__.py` - Export DataProfiler classes
- ✅ `examples/demo_pipelines/financial_validation_demo.py` - Integrated profiling
