"""
Validation Agent
Monitors data transformations end-to-end, validates business logic implementation,
and performs regression testing on pipeline changes.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Model for validation result"""
    rule_name: str = Field(description="Name of the validation rule")
    status: str = Field(description="Status (passed, failed, warning)")
    message: str = Field(description="Validation message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    timestamp: str = Field(description="When validation was performed")


class PipelineValidationReport(BaseModel):
    """Model for complete pipeline validation report"""
    pipeline_name: str = Field(description="Name of the pipeline")
    validation_results: List[ValidationResult] = Field(description="List of validation results")
    overall_status: str = Field(description="Overall status (passed, failed, warning)")
    summary: Dict[str, int] = Field(description="Summary statistics")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class ValidationAgent:
    """
    AI Agent responsible for validating data transformations and monitoring
    pipeline quality.
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.3):
        """
        Initialize the Validation Agent
        
        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature for LLM responses (lower for more deterministic)
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        
    def validate_schema_compliance(self, data: Dict[str, Any], 
                                   schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate that data complies with the expected schema
        
        Args:
            data: Data to validate
            schema: Expected schema
            
        Returns:
            Validation result
        """
        issues = []
        
        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
            elif data[field] is None:
                issues.append(f"Required field is null: {field}")
        
        # Check data types
        for field_name, field_spec in schema.get("properties", {}).items():
            if field_name in data and data[field_name] is not None:
                expected_type = field_spec.get("type")
                actual_value = data[field_name]
                
                if not self._check_type(actual_value, expected_type):
                    issues.append(
                        f"Type mismatch for {field_name}: expected {expected_type}, "
                        f"got {type(actual_value).__name__}"
                    )
        
        status = "failed" if issues else "passed"
        message = "; ".join(issues) if issues else "Schema validation passed"
        
        return ValidationResult(
            rule_name="schema_compliance",
            status=status,
            message=message,
            details={"issues": issues, "fields_checked": len(schema.get("properties", {}))},
            timestamp=datetime.now().isoformat()
        )
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type, str)
        return isinstance(value, expected_python_type)
    
    def validate_business_rules(self, data: Dict[str, Any], 
                                rules: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Validate data against business rules
        
        Args:
            data: Data to validate
            rules: List of business rules
            
        Returns:
            List of validation results
        """
        results = []
        
        for rule in rules:
            rule_name = rule.get("name", "unnamed_rule")
            rule_type = rule.get("type", "custom")
            rule_expression = rule.get("expression", "")
            
            try:
                if rule_type == "range":
                    field = rule.get("field")
                    min_val = rule.get("min")
                    max_val = rule.get("max")
                    
                    value = data.get(field)
                    if value is not None:
                        if min_val is not None and value < min_val:
                            results.append(ValidationResult(
                                rule_name=rule_name,
                                status="failed",
                                message=f"{field} value {value} is below minimum {min_val}",
                                details={"field": field, "value": value, "min": min_val},
                                timestamp=datetime.now().isoformat()
                            ))
                        elif max_val is not None and value > max_val:
                            results.append(ValidationResult(
                                rule_name=rule_name,
                                status="failed",
                                message=f"{field} value {value} exceeds maximum {max_val}",
                                details={"field": field, "value": value, "max": max_val},
                                timestamp=datetime.now().isoformat()
                            ))
                        else:
                            results.append(ValidationResult(
                                rule_name=rule_name,
                                status="passed",
                                message=f"{field} is within valid range",
                                details={"field": field, "value": value},
                                timestamp=datetime.now().isoformat()
                            ))
                            
                elif rule_type == "pattern":
                    import re
                    field = rule.get("field")
                    pattern = rule.get("pattern")
                    
                    value = str(data.get(field, ""))
                    if re.match(pattern, value):
                        results.append(ValidationResult(
                            rule_name=rule_name,
                            status="passed",
                            message=f"{field} matches pattern",
                            details={"field": field, "pattern": pattern},
                            timestamp=datetime.now().isoformat()
                        ))
                    else:
                        results.append(ValidationResult(
                            rule_name=rule_name,
                            status="failed",
                            message=f"{field} does not match pattern {pattern}",
                            details={"field": field, "value": value, "pattern": pattern},
                            timestamp=datetime.now().isoformat()
                        ))
                        
                elif rule_type == "custom":
                    # Use AI to evaluate custom business rules
                    result = self._evaluate_custom_rule(data, rule_expression, rule_name)
                    results.append(result)
                    
            except Exception as e:
                results.append(ValidationResult(
                    rule_name=rule_name,
                    status="failed",
                    message=f"Error evaluating rule: {str(e)}",
                    details={"error": str(e)},
                    timestamp=datetime.now().isoformat()
                ))
        
        return results
    
    def _evaluate_custom_rule(self, data: Dict[str, Any], 
                             expression: str, rule_name: str) -> ValidationResult:
        """Evaluate custom business rule using AI"""
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a business logic validator. Evaluate whether the data 
            satisfies the given business rule. Respond with JSON containing:
            {{"status": "passed" or "failed", "message": "explanation"}}"""),
            ("user", """Data: {data}
            
            Business Rule: {expression}
            
            Evaluate and respond in JSON format.""")
        ])
        
        chain = prompt_template | self.llm
        response = chain.invoke({
            "data": json.dumps(data, indent=2),
            "expression": expression
        })
        
        try:
            result = json.loads(response.content)
            return ValidationResult(
                rule_name=rule_name,
                status=result.get("status", "failed"),
                message=result.get("message", "Custom rule evaluation"),
                details={"expression": expression},
                timestamp=datetime.now().isoformat()
            )
        except json.JSONDecodeError:
            return ValidationResult(
                rule_name=rule_name,
                status="failed",
                message="Failed to parse AI response",
                details={"response": response.content},
                timestamp=datetime.now().isoformat()
            )
    
    def validate_transformation(self, source_data: Dict[str, Any],
                               transformed_data: Dict[str, Any],
                               transformation_rules: List[str]) -> PipelineValidationReport:
        """
        Validate that data transformation was performed correctly
        
        Args:
            source_data: Original data before transformation
            transformed_data: Data after transformation
            transformation_rules: Expected transformation rules
            
        Returns:
            Validation report
        """
        validation_results = []
        
        # Check data integrity
        validation_results.append(
            ValidationResult(
                rule_name="data_integrity",
                status="passed" if transformed_data else "failed",
                message="Transformed data exists" if transformed_data else "No transformed data",
                details={"record_count": len(transformed_data) if isinstance(transformed_data, list) else 1},
                timestamp=datetime.now().isoformat()
            )
        )
        
        # Use AI to validate transformations
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a data transformation validator. Analyze if the transformation 
            was performed correctly according to the rules. Identify any discrepancies."""),
            ("user", """Source Data: {source}
            
            Transformed Data: {transformed}
            
            Expected Transformation Rules: {rules}
            
            Validate the transformation and list any issues found. Respond in JSON format:
            {{"issues": ["issue1", "issue2"], "status": "passed" or "failed"}}""")
        ])
        
        chain = prompt_template | self.llm
        response = chain.invoke({
            "source": json.dumps(source_data, indent=2)[:1000],  # Limit size
            "transformed": json.dumps(transformed_data, indent=2)[:1000],
            "rules": json.dumps(transformation_rules, indent=2)
        })
        
        try:
            ai_result = json.loads(response.content)
            validation_results.append(
                ValidationResult(
                    rule_name="transformation_logic",
                    status=ai_result.get("status", "warning"),
                    message="; ".join(ai_result.get("issues", ["Validation completed"])),
                    details=ai_result,
                    timestamp=datetime.now().isoformat()
                )
            )
        except json.JSONDecodeError:
            validation_results.append(
                ValidationResult(
                    rule_name="transformation_logic",
                    status="warning",
                    message="Could not parse AI validation response",
                    details={"response": response.content[:200]},
                    timestamp=datetime.now().isoformat()
                )
            )
        
        # Calculate summary
        summary = {
            "passed": sum(1 for r in validation_results if r.status == "passed"),
            "failed": sum(1 for r in validation_results if r.status == "failed"),
            "warning": sum(1 for r in validation_results if r.status == "warning")
        }
        
        overall_status = "failed" if summary["failed"] > 0 else "passed"
        
        return PipelineValidationReport(
            pipeline_name="transformation_validation",
            validation_results=validation_results,
            overall_status=overall_status,
            summary=summary,
            recommendations=self._generate_recommendations(validation_results)
        )
    
    def perform_regression_test(self, baseline_results: List[Dict[str, Any]],
                               current_results: List[Dict[str, Any]]) -> PipelineValidationReport:
        """
        Compare current pipeline results against baseline to detect regressions
        
        Args:
            baseline_results: Historical baseline test results
            current_results: Current test results
            
        Returns:
            Regression test report
        """
        validation_results = []
        
        # Compare result counts
        baseline_count = len(baseline_results)
        current_count = len(current_results)
        
        if baseline_count != current_count:
            validation_results.append(
                ValidationResult(
                    rule_name="result_count",
                    status="warning",
                    message=f"Result count changed from {baseline_count} to {current_count}",
                    details={"baseline": baseline_count, "current": current_count},
                    timestamp=datetime.now().isoformat()
                )
            )
        else:
            validation_results.append(
                ValidationResult(
                    rule_name="result_count",
                    status="passed",
                    message=f"Result count unchanged: {current_count}",
                    details={"count": current_count},
                    timestamp=datetime.now().isoformat()
                )
            )
        
        # Use AI to detect semantic changes
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a regression testing expert. Compare baseline and current results
            to identify any regressions, improvements, or significant changes."""),
            ("user", """Baseline Results: {baseline}
            
            Current Results: {current}
            
            Identify regressions and changes. Respond in JSON:
            {{"regressions": [], "improvements": [], "status": "passed/failed"}}""")
        ])
        
        chain = prompt_template | self.llm
        response = chain.invoke({
            "baseline": json.dumps(baseline_results[:5], indent=2),  # Sample
            "current": json.dumps(current_results[:5], indent=2)
        })
        
        try:
            ai_result = json.loads(response.content)
            regressions = ai_result.get("regressions", [])
            
            validation_results.append(
                ValidationResult(
                    rule_name="regression_detection",
                    status="failed" if regressions else "passed",
                    message=f"Found {len(regressions)} regressions" if regressions else "No regressions detected",
                    details=ai_result,
                    timestamp=datetime.now().isoformat()
                )
            )
        except json.JSONDecodeError:
            validation_results.append(
                ValidationResult(
                    rule_name="regression_detection",
                    status="warning",
                    message="Could not parse regression analysis",
                    details={},
                    timestamp=datetime.now().isoformat()
                )
            )
        
        summary = {
            "passed": sum(1 for r in validation_results if r.status == "passed"),
            "failed": sum(1 for r in validation_results if r.status == "failed"),
            "warning": sum(1 for r in validation_results if r.status == "warning")
        }
        
        return PipelineValidationReport(
            pipeline_name="regression_testing",
            validation_results=validation_results,
            overall_status="failed" if summary["failed"] > 0 else "passed",
            summary=summary,
            recommendations=self._generate_recommendations(validation_results)
        )
    
    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        failed_results = [r for r in results if r.status == "failed"]
        
        if failed_results:
            recommendations.append(
                f"Address {len(failed_results)} failed validations before deploying to production"
            )
            
        warning_results = [r for r in results if r.status == "warning"]
        if warning_results:
            recommendations.append(
                f"Review {len(warning_results)} warnings for potential issues"
            )
            
        return recommendations
    
    def monitor_data_quality(self, data: List[Dict[str, Any]], 
                           quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor ongoing data quality metrics
        
        Args:
            data: Data to monitor
            quality_metrics: Quality metrics configuration
            
        Returns:
            Quality monitoring report
        """
        metrics = {
            "total_records": len(data),
            "null_counts": {},
            "duplicate_count": 0,
            "completeness_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        if not data:
            return metrics
        
        # Calculate null counts
        fields = data[0].keys() if data else []
        for field in fields:
            null_count = sum(1 for record in data if record.get(field) is None)
            metrics["null_counts"][field] = null_count
        
        # Calculate completeness
        total_fields = len(data) * len(fields)
        total_nulls = sum(metrics["null_counts"].values())
        metrics["completeness_score"] = (total_fields - total_nulls) / total_fields if total_fields > 0 else 0
        
        return metrics
