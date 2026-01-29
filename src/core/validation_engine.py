"""
Validation Engine
Core validation logic for executing test cases and validating data quality.
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import re


class ValidationRule:
    """Represents a single validation rule"""
    
    def __init__(self, name: str, description: str, 
                 validator: Callable[[Any], bool], 
                 error_message: str):
        """
        Initialize a validation rule
        
        Args:
            name: Rule name
            description: Rule description
            validator: Function that returns True if validation passes
            error_message: Message to show when validation fails
        """
        self.name = name
        self.description = description
        self.validator = validator
        self.error_message = error_message
    
    def validate(self, value: Any) -> Dict[str, Any]:
        """
        Execute validation
        
        Returns:
            Validation result dictionary
        """
        try:
            passed = self.validator(value)
            return {
                "rule": self.name,
                "passed": passed,
                "message": None if passed else self.error_message,
                "value": str(value)[:100],  # Truncate long values
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "rule": self.name,
                "passed": False,
                "message": f"Validation error: {str(e)}",
                "value": str(value)[:100],
                "timestamp": datetime.now().isoformat()
            }


class ValidationEngine:
    """
    Core engine for executing validation rules and test cases.
    """
    
    def __init__(self):
        """Initialize the Validation Engine"""
        self.built_in_rules = self._create_built_in_rules()
        self.custom_rules = []
        
    def _create_built_in_rules(self) -> Dict[str, ValidationRule]:
        """Create built-in validation rules"""
        return {
            "not_null": ValidationRule(
                "not_null",
                "Value must not be null",
                lambda v: v is not None,
                "Value is null"
            ),
            "not_empty": ValidationRule(
                "not_empty",
                "Value must not be empty",
                lambda v: v is not None and (len(str(v)) > 0 if hasattr(v, '__len__') or isinstance(v, str) else True),
                "Value is empty"
            ),
            "is_string": ValidationRule(
                "is_string",
                "Value must be a string",
                lambda v: isinstance(v, str),
                "Value is not a string"
            ),
            "is_integer": ValidationRule(
                "is_integer",
                "Value must be an integer",
                lambda v: isinstance(v, int) and not isinstance(v, bool),
                "Value is not an integer"
            ),
            "is_number": ValidationRule(
                "is_number",
                "Value must be a number",
                lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
                "Value is not a number"
            ),
            "is_boolean": ValidationRule(
                "is_boolean",
                "Value must be a boolean",
                lambda v: isinstance(v, bool),
                "Value is not a boolean"
            ),
            "is_array": ValidationRule(
                "is_array",
                "Value must be an array",
                lambda v: isinstance(v, list),
                "Value is not an array"
            ),
            "is_object": ValidationRule(
                "is_object",
                "Value must be an object",
                lambda v: isinstance(v, dict),
                "Value is not an object"
            )
        }
    
    def add_custom_rule(self, rule: ValidationRule):
        """Add a custom validation rule"""
        self.custom_rules.append(rule)
    
    def validate_schema_compliance(self, data: Dict[str, Any],
                                   schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema: Schema definition
            
        Returns:
            Validation results
        """
        results = {
            "overall_status": "passed",
            "validations": [],
            "errors": [],
            "warnings": [],
            "validated_at": datetime.now().isoformat()
        }
        
        # Validate required fields
        for field in schema.get("required", []):
            if field not in data:
                results["errors"].append(f"Missing required field: {field}")
                results["overall_status"] = "failed"
            elif data[field] is None:
                results["errors"].append(f"Required field is null: {field}")
                results["overall_status"] = "failed"
        
        # Validate each field
        for field_name, field_spec in schema.get("properties", {}).items():
            if field_name in data:
                field_results = self._validate_field(
                    field_name, 
                    data[field_name], 
                    field_spec
                )
                results["validations"].append(field_results)
                
                if not field_results["passed"]:
                    results["overall_status"] = "failed"
        
        return results
    
    def _validate_field(self, field_name: str, value: Any,
                       field_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single field
        
        Returns:
            Field validation results
        """
        field_type = field_spec.get("type", "string")
        validations = []
        
        # Type validation
        type_rule = self._get_type_rule(field_type)
        if type_rule:
            validations.append(type_rule.validate(value))
        
        # Type-specific validations
        if field_type in ["integer", "number"]:
            validations.extend(self._validate_numeric(value, field_spec))
        elif field_type == "string":
            validations.extend(self._validate_string(value, field_spec))
        elif field_type == "array":
            validations.extend(self._validate_array(value, field_spec))
        
        # Enum validation
        if "enum" in field_spec:
            validations.append(self._validate_enum(value, field_spec["enum"]))
        
        passed = all(v["passed"] for v in validations)
        
        return {
            "field": field_name,
            "passed": passed,
            "validations": validations,
            "errors": [v["message"] for v in validations if not v["passed"]]
        }
    
    def _get_type_rule(self, field_type: str) -> Optional[ValidationRule]:
        """Get validation rule for type"""
        type_map = {
            "string": "is_string",
            "integer": "is_integer",
            "number": "is_number",
            "boolean": "is_boolean",
            "array": "is_array",
            "object": "is_object"
        }
        rule_name = type_map.get(field_type)
        return self.built_in_rules.get(rule_name) if rule_name else None
    
    def _validate_numeric(self, value: Any, field_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate numeric constraints"""
        results = []
        
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return results
        
        # Minimum
        if "minimum" in field_spec:
            minimum = field_spec["minimum"]
            rule = ValidationRule(
                "minimum",
                f"Value must be >= {minimum}",
                lambda v: v >= minimum,
                f"Value {value} is less than minimum {minimum}"
            )
            results.append(rule.validate(value))
        
        # Maximum
        if "maximum" in field_spec:
            maximum = field_spec["maximum"]
            rule = ValidationRule(
                "maximum",
                f"Value must be <= {maximum}",
                lambda v: v <= maximum,
                f"Value {value} exceeds maximum {maximum}"
            )
            results.append(rule.validate(value))
        
        # Multiple of
        if "multipleOf" in field_spec:
            multiple_of = field_spec["multipleOf"]
            rule = ValidationRule(
                "multipleOf",
                f"Value must be multiple of {multiple_of}",
                lambda v: v % multiple_of == 0,
                f"Value {value} is not a multiple of {multiple_of}"
            )
            results.append(rule.validate(value))
        
        return results
    
    def _validate_string(self, value: Any, field_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate string constraints"""
        results = []
        
        if not isinstance(value, str):
            return results
        
        # Min length
        if "minLength" in field_spec:
            min_length = field_spec["minLength"]
            rule = ValidationRule(
                "minLength",
                f"String length must be >= {min_length}",
                lambda v: len(v) >= min_length,
                f"String length {len(value)} is less than minimum {min_length}"
            )
            results.append(rule.validate(value))
        
        # Max length
        if "maxLength" in field_spec:
            max_length = field_spec["maxLength"]
            rule = ValidationRule(
                "maxLength",
                f"String length must be <= {max_length}",
                lambda v: len(v) <= max_length,
                f"String length {len(value)} exceeds maximum {max_length}"
            )
            results.append(rule.validate(value))
        
        # Pattern
        if "pattern" in field_spec:
            pattern = field_spec["pattern"]
            rule = ValidationRule(
                "pattern",
                f"String must match pattern {pattern}",
                lambda v: re.match(pattern, v) is not None,
                f"String does not match pattern {pattern}"
            )
            results.append(rule.validate(value))
        
        # Format
        if "format" in field_spec:
            format_type = field_spec["format"]
            results.append(self._validate_format(value, format_type))
        
        return results
    
    def _validate_array(self, value: Any, field_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate array constraints"""
        results = []
        
        if not isinstance(value, list):
            return results
        
        # Min items
        if "minItems" in field_spec:
            min_items = field_spec["minItems"]
            rule = ValidationRule(
                "minItems",
                f"Array must have >= {min_items} items",
                lambda v: len(v) >= min_items,
                f"Array has {len(value)} items, minimum is {min_items}"
            )
            results.append(rule.validate(value))
        
        # Max items
        if "maxItems" in field_spec:
            max_items = field_spec["maxItems"]
            rule = ValidationRule(
                "maxItems",
                f"Array must have <= {max_items} items",
                lambda v: len(v) <= max_items,
                f"Array has {len(value)} items, maximum is {max_items}"
            )
            results.append(rule.validate(value))
        
        # Unique items
        if field_spec.get("uniqueItems", False):
            rule = ValidationRule(
                "uniqueItems",
                "Array items must be unique",
                lambda v: len(v) == len(set(str(item) for item in v)),
                "Array contains duplicate items"
            )
            results.append(rule.validate(value))
        
        return results
    
    def _validate_enum(self, value: Any, enum_values: List[Any]) -> Dict[str, Any]:
        """Validate enum constraint"""
        rule = ValidationRule(
            "enum",
            f"Value must be one of {enum_values}",
            lambda v: v in enum_values,
            f"Value {value} is not in allowed values {enum_values}"
        )
        return rule.validate(value)
    
    def _validate_format(self, value: str, format_type: str) -> Dict[str, Any]:
        """Validate string format"""
        format_patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "uri": r"^https?://",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "date-time": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
            "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        }
        
        pattern = format_patterns.get(format_type)
        if pattern:
            rule = ValidationRule(
                f"format_{format_type}",
                f"String must be valid {format_type}",
                lambda v: re.match(pattern, v, re.IGNORECASE) is not None,
                f"String is not a valid {format_type}"
            )
            return rule.validate(value)
        
        return {
            "rule": f"format_{format_type}",
            "passed": True,
            "message": f"Format {format_type} not validated (unknown format)",
            "value": value[:100],
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_test_suite(self, test_cases: List[Dict[str, Any]],
                          data: List[Dict[str, Any]],
                          schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete test suite
        
        Args:
            test_cases: List of test cases to execute
            data: Data to test
            schema: Schema for validation
            
        Returns:
            Test execution results
        """
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_results": [],
            "executed_at": datetime.now().isoformat()
        }
        
        for test_case in test_cases:
            try:
                # Execute test
                test_result = self.validate_schema_compliance(
                    test_case.get("test_data", {}),
                    schema
                )
                
                passed = test_result["overall_status"] == "passed"
                expected_outcome = test_case.get("expected_outcome", "pass")
                
                # Check if result matches expectation
                test_passed = (
                    (passed and expected_outcome == "pass") or
                    (not passed and expected_outcome == "fail")
                )
                
                if test_passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                
                results["test_results"].append({
                    "test_name": test_case.get("test_name"),
                    "test_type": test_case.get("test_type"),
                    "passed": test_passed,
                    "details": test_result
                })
                
            except Exception as e:
                results["errors"] += 1
                results["test_results"].append({
                    "test_name": test_case.get("test_name"),
                    "passed": False,
                    "error": str(e)
                })
        
        results["pass_rate"] = (results["passed"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
        
        return results
