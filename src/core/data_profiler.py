"""
Data Profiler: Profile datasets and detect anomalies
Provides comprehensive data profiling, drift detection, and anomaly identification
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from collections import Counter


@dataclass
class ProfileResult:
    """Profile statistics for a single column"""
    column_name: str
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    distinct_count: int
    distinct_percentage: float
    min_value: Any = None
    max_value: Any = None
    mean_value: Any = None
    median_value: Any = None
    std_dev: Any = None
    top_values: List[tuple] = None  # (value, count) tuples
    anomalies: List[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class DatasetProfile:
    """Complete profile for a dataset"""
    total_records: int
    total_columns: int
    column_profiles: Dict[str, ProfileResult]
    profile_timestamp: str
    dataset_name: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "total_records": self.total_records,
            "total_columns": self.total_columns,
            "column_profiles": {k: v.to_dict() for k, v in self.column_profiles.items()},
            "profile_timestamp": self.profile_timestamp,
            "dataset_name": self.dataset_name
        }
    
    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class DriftResult:
    """Drift detection result for a single column"""
    column_name: str
    has_drift: bool
    drift_score: float
    null_percentage_drift: float
    distinct_count_drift: int
    value_distribution_drift: float
    drift_details: List[str]


class DataProfiler:
    """
    Profile datasets and detect anomalies
    
    Features:
    - Comprehensive column profiling (nulls, distinct values, distributions)
    - Data drift detection (comparing baseline vs current)
    - Anomaly detection (outliers, unexpected patterns)
    - Support for numeric, categorical, and temporal data
    """
    
    def __init__(self, drift_threshold: float = 0.1):
        """
        Initialize profiler
        
        Args:
            drift_threshold: Threshold for detecting significant drift (0-1)
        """
        self.drift_threshold = drift_threshold
    
    def profile_dataset(
        self, 
        data: List[Dict], 
        dataset_name: Optional[str] = None
    ) -> DatasetProfile:
        """
        Generate comprehensive data profile
        
        Args:
            data: List of dictionaries representing records
            dataset_name: Optional name for the dataset
            
        Returns:
            DatasetProfile containing all profiling information
        """
        if not data:
            raise ValueError("Cannot profile empty dataset")
        
        column_profiles = {}
        
        # Get all unique column names
        all_columns = set()
        for record in data:
            all_columns.update(record.keys())
        
        # Profile each column
        for column in sorted(all_columns):
            column_profiles[column] = self._profile_column(column, data)
        
        return DatasetProfile(
            total_records=len(data),
            total_columns=len(all_columns),
            column_profiles=column_profiles,
            profile_timestamp=datetime.now().isoformat(),
            dataset_name=dataset_name
        )
    
    def _profile_column(self, column_name: str, data: List[Dict]) -> ProfileResult:
        """Profile a single column"""
        values = [record.get(column_name) for record in data]
        total_count = len(values)
        
        # Count nulls
        null_count = sum(1 for v in values if v is None or v == "")
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
        
        # Non-null values
        non_null_values = [v for v in values if v is not None and v != ""]
        
        # Distinct values - handle unhashable types (lists, dicts)
        try:
            distinct_count = len(set(non_null_values)) if non_null_values else 0
        except TypeError:
            # For unhashable types, convert to string representation
            distinct_count = len(set(str(v) for v in non_null_values)) if non_null_values else 0
        distinct_percentage = (distinct_count / total_count * 100) if total_count > 0 else 0
        
        # Determine data type
        data_type = self._infer_type(non_null_values)
        
        # Initialize stats
        min_value = None
        max_value = None
        mean_value = None
        median_value = None
        std_dev = None
        top_values = None
        anomalies = []
        
        if non_null_values:
            # Numeric statistics
            if data_type in ["integer", "float", "number"]:
                try:
                    numeric_values = [float(v) for v in non_null_values if self._is_numeric(v)]
                    if numeric_values:
                        min_value = min(numeric_values)
                        max_value = max(numeric_values)
                        mean_value = sum(numeric_values) / len(numeric_values)
                        median_value = self._calculate_median(numeric_values)
                        std_dev = self._calculate_std_dev(numeric_values, mean_value)
                        
                        # Detect numeric anomalies
                        anomalies.extend(self._detect_numeric_anomalies(
                            numeric_values, mean_value, std_dev
                        ))
                except (ValueError, TypeError):
                    pass
            
            # Top values for categorical data
            if data_type in ["string", "boolean"] or distinct_count < 20:
                try:
                    value_counts = Counter(non_null_values)
                    top_values = value_counts.most_common(10)
                except TypeError:
                    # For unhashable types, convert to string
                    value_counts = Counter(str(v) for v in non_null_values)
                    top_values = value_counts.most_common(10)
            
            # String-specific checks
            if data_type == "string":
                min_value = min(len(str(v)) for v in non_null_values)
                max_value = max(len(str(v)) for v in non_null_values)
                mean_value = sum(len(str(v)) for v in non_null_values) / len(non_null_values)
        
        # Data quality anomalies
        if null_percentage > 50:
            anomalies.append(f"High null percentage: {null_percentage:.1f}%")
        
        if distinct_count == total_count and total_count > 10:
            anomalies.append("All values are unique (possible unique identifier)")
        
        if distinct_count == 1 and total_count > 1:
            anomalies.append("All values are identical (constant column)")
        
        return ProfileResult(
            column_name=column_name,
            data_type=data_type,
            total_count=total_count,
            null_count=null_count,
            null_percentage=null_percentage,
            distinct_count=distinct_count,
            distinct_percentage=distinct_percentage,
            min_value=min_value,
            max_value=max_value,
            mean_value=mean_value,
            median_value=median_value,
            std_dev=std_dev,
            top_values=top_values,
            anomalies=anomalies if anomalies else None
        )
    
    def detect_drift(
        self, 
        baseline_profile: DatasetProfile, 
        current_data: List[Dict]
    ) -> Dict[str, DriftResult]:
        """
        Compare current data against baseline profile to detect drift
        
        Args:
            baseline_profile: Baseline DatasetProfile
            current_data: Current dataset to compare
            
        Returns:
            Dictionary mapping column names to DriftResult
        """
        current_profile = self.profile_dataset(current_data, dataset_name="current")
        drift_report = {}
        
        for column, baseline in baseline_profile.column_profiles.items():
            if column not in current_profile.column_profiles:
                drift_report[column] = DriftResult(
                    column_name=column,
                    has_drift=True,
                    drift_score=1.0,
                    null_percentage_drift=0,
                    distinct_count_drift=0,
                    value_distribution_drift=0,
                    drift_details=[f"Column {column} missing from current dataset"]
                )
                continue
            
            current = current_profile.column_profiles[column]
            drift_details = []
            
            # Null percentage drift
            null_drift = abs(current.null_percentage - baseline.null_percentage)
            if null_drift > self.drift_threshold * 100:
                drift_details.append(
                    f"Null percentage changed from {baseline.null_percentage:.1f}% "
                    f"to {current.null_percentage:.1f}%"
                )
            
            # Distinct count drift
            distinct_drift = abs(current.distinct_count - baseline.distinct_count)
            distinct_drift_pct = (distinct_drift / baseline.distinct_count * 100) if baseline.distinct_count > 0 else 0
            if distinct_drift_pct > self.drift_threshold * 100:
                drift_details.append(
                    f"Distinct values changed from {baseline.distinct_count} "
                    f"to {current.distinct_count} ({distinct_drift_pct:.1f}% change)"
                )
            
            # Value distribution drift (for categorical)
            value_drift = 0.0
            if baseline.top_values and current.top_values:
                value_drift = self._calculate_distribution_drift(
                    baseline.top_values, current.top_values
                )
                if value_drift > self.drift_threshold:
                    drift_details.append(
                        f"Value distribution changed (drift score: {value_drift:.2f})"
                    )
            
            # Numeric range drift
            if baseline.data_type in ["integer", "float", "number"]:
                if baseline.mean_value and current.mean_value:
                    mean_drift_pct = abs(current.mean_value - baseline.mean_value) / baseline.mean_value * 100
                    if mean_drift_pct > self.drift_threshold * 100:
                        drift_details.append(
                            f"Mean value changed from {baseline.mean_value:.2f} "
                            f"to {current.mean_value:.2f} ({mean_drift_pct:.1f}% change)"
                        )
            
            # Calculate overall drift score
            drift_score = max(
                null_drift / 100,
                distinct_drift_pct / 100,
                value_drift
            )
            
            drift_report[column] = DriftResult(
                column_name=column,
                has_drift=bool(drift_details),
                drift_score=drift_score,
                null_percentage_drift=null_drift,
                distinct_count_drift=distinct_drift,
                value_distribution_drift=value_drift,
                drift_details=drift_details if drift_details else ["No significant drift detected"]
            )
        
        # Check for new columns in current data
        for column in current_profile.column_profiles:
            if column not in baseline_profile.column_profiles:
                drift_report[column] = DriftResult(
                    column_name=column,
                    has_drift=True,
                    drift_score=1.0,
                    null_percentage_drift=0,
                    distinct_count_drift=0,
                    value_distribution_drift=0,
                    drift_details=[f"New column {column} appeared in current dataset"]
                )
        
        return drift_report
    
    def find_anomalies(
        self, 
        data: List[Dict], 
        column: str,
        method: str = "iqr"
    ) -> List[Dict]:
        """
        Identify anomalous records using statistical methods
        
        Args:
            data: Dataset to analyze
            column: Column to check for anomalies
            method: Detection method ("iqr", "zscore")
            
        Returns:
            List of anomalous records with scores
        """
        values = [(i, record.get(column)) for i, record in enumerate(data)]
        numeric_values = [(i, float(v)) for i, v in values if self._is_numeric(v)]
        
        if not numeric_values:
            return []
        
        indices, nums = zip(*numeric_values)
        anomalous_records = []
        
        if method == "iqr":
            # Interquartile Range method
            q1 = self._calculate_percentile(nums, 25)
            q3 = self._calculate_percentile(nums, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            for idx, value in zip(indices, nums):
                if value < lower_bound or value > upper_bound:
                    anomalous_records.append({
                        "record_index": idx,
                        "record": data[idx],
                        "anomaly_value": value,
                        "anomaly_score": abs(value - ((lower_bound + upper_bound) / 2)),
                        "reason": f"Value {value} outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]"
                    })
        
        elif method == "zscore":
            # Z-score method
            mean = sum(nums) / len(nums)
            std_dev = self._calculate_std_dev(nums, mean)
            
            if std_dev > 0:
                for idx, value in zip(indices, nums):
                    z_score = abs((value - mean) / std_dev)
                    if z_score > 3:  # More than 3 standard deviations
                        anomalous_records.append({
                            "record_index": idx,
                            "record": data[idx],
                            "anomaly_value": value,
                            "anomaly_score": z_score,
                            "reason": f"Z-score {z_score:.2f} exceeds threshold (3.0)"
                        })
        
        return sorted(anomalous_records, key=lambda x: x["anomaly_score"], reverse=True)
    
    def _infer_type(self, values: List[Any]) -> str:
        """Infer the data type of a list of values"""
        if not values:
            return "unknown"
        
        sample = values[:100]  # Use first 100 values for type inference
        
        # Check if boolean
        if all(isinstance(v, bool) for v in sample):
            return "boolean"
        
        # Check if numeric
        if all(self._is_numeric(v) for v in sample):
            if all(isinstance(v, int) or (isinstance(v, float) and v.is_integer()) for v in sample):
                return "integer"
            return "float"
        
        # Check if datetime-like
        if all(isinstance(v, (datetime,)) or self._is_date_string(v) for v in sample):
            return "datetime"
        
        return "string"
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_date_string(self, value: Any) -> bool:
        """Check if value is a date string"""
        if not isinstance(value, str):
            return False
        
        # Simple heuristic - check for common date patterns
        date_indicators = ['-', '/', 'T', ':']
        return any(indicator in value for indicator in date_indicators) and len(value) >= 8
    
    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median of a list of values"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        return sorted_values[n // 2]
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of a list of values"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _calculate_std_dev(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _detect_numeric_anomalies(
        self, 
        values: List[float], 
        mean: float, 
        std_dev: float
    ) -> List[str]:
        """Detect anomalies in numeric data"""
        anomalies = []
        
        if std_dev > 0:
            outliers = [v for v in values if abs(v - mean) > 3 * std_dev]
            if outliers:
                anomalies.append(
                    f"Found {len(outliers)} outliers (>3 std dev from mean)"
                )
        
        # Check for suspiciously round numbers
        round_count = sum(1 for v in values if v == round(v, 0))
        if round_count / len(values) > 0.9 and len(values) > 10:
            anomalies.append("High proportion of round numbers (possible data quality issue)")
        
        return anomalies
    
    def _calculate_distribution_drift(
        self, 
        baseline_top: List[tuple], 
        current_top: List[tuple]
    ) -> float:
        """Calculate drift score for categorical distributions"""
        baseline_dict = dict(baseline_top)
        current_dict = dict(current_top)
        
        all_values = set(baseline_dict.keys()) | set(current_dict.keys())
        
        baseline_total = sum(baseline_dict.values())
        current_total = sum(current_dict.values())
        
        drift_score = 0.0
        for value in all_values:
            baseline_freq = baseline_dict.get(value, 0) / baseline_total
            current_freq = current_dict.get(value, 0) / current_total
            drift_score += abs(baseline_freq - current_freq)
        
        return drift_score / 2  # Normalize to 0-1 range
