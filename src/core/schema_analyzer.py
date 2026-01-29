"""
Schema Analyzer
Analyzes data schemas to extract metadata, constraints, and business rules.
Supports JSON Schema, Avro, and custom schema formats.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json


class SchemaAnalyzer:
    """
    Analyzes data schemas to extract insights for test generation and validation.
    """
    
    def __init__(self):
        """Initialize the Schema Analyzer"""
        self.supported_types = {
            "string", "integer", "number", "boolean", "array", "object", "null"
        }
        
    def analyze(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive schema analysis
        
        Args:
            schema: Schema definition (JSON Schema format)
            
        Returns:
            Analysis results with metadata and insights
        """
        analysis = {
            "schema_type": self._detect_schema_type(schema),
            "field_count": len(schema.get("properties", {})),
            "required_fields": schema.get("required", []),
            "optional_fields": self._get_optional_fields(schema),
            "field_analysis": self._analyze_fields(schema),
            "constraints": self._extract_constraints(schema),
            "complexity_score": self._calculate_complexity(schema),
            "test_recommendations": self._generate_test_recommendations(schema),
            "analyzed_at": datetime.now().isoformat()
        }
        
        return analysis
    
    def _detect_schema_type(self, schema: Dict[str, Any]) -> str:
        """Detect the type of schema format"""
        if "$schema" in schema:
            return "json_schema"
        elif "type" in schema and schema["type"] == "record":
            return "avro"
        else:
            return "custom"
    
    def _get_optional_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Get list of optional fields"""
        all_fields = set(schema.get("properties", {}).keys())
        required_fields = set(schema.get("required", []))
        return list(all_fields - required_fields)
    
    def _analyze_fields(self, schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze each field in the schema
        
        Returns:
            Dictionary mapping field names to their analysis
        """
        field_analysis = {}
        
        for field_name, field_spec in schema.get("properties", {}).items():
            field_type = field_spec.get("type", "unknown")
            
            analysis = {
                "type": field_type,
                "required": field_name in schema.get("required", []),
                "nullable": "null" in field_type if isinstance(field_type, list) else False,
                "has_constraints": self._has_constraints(field_spec),
                "constraints": self._get_field_constraints(field_spec),
                "test_priority": self._determine_test_priority(field_name, field_spec, schema)
            }
            
            # Add type-specific analysis
            if field_type in ["integer", "number"]:
                analysis["numeric_constraints"] = {
                    "minimum": field_spec.get("minimum"),
                    "maximum": field_spec.get("maximum"),
                    "exclusive_minimum": field_spec.get("exclusiveMinimum"),
                    "exclusive_maximum": field_spec.get("exclusiveMaximum"),
                    "multiple_of": field_spec.get("multipleOf")
                }
            elif field_type == "string":
                analysis["string_constraints"] = {
                    "min_length": field_spec.get("minLength"),
                    "max_length": field_spec.get("maxLength"),
                    "pattern": field_spec.get("pattern"),
                    "format": field_spec.get("format"),
                    "enum": field_spec.get("enum")
                }
            elif field_type == "array":
                analysis["array_constraints"] = {
                    "min_items": field_spec.get("minItems"),
                    "max_items": field_spec.get("maxItems"),
                    "unique_items": field_spec.get("uniqueItems"),
                    "items_type": field_spec.get("items", {}).get("type")
                }
            
            field_analysis[field_name] = analysis
        
        return field_analysis
    
    def _has_constraints(self, field_spec: Dict[str, Any]) -> bool:
        """Check if field has any constraints"""
        constraint_keywords = [
            "minimum", "maximum", "minLength", "maxLength", "pattern",
            "format", "enum", "minItems", "maxItems", "uniqueItems"
        ]
        return any(keyword in field_spec for keyword in constraint_keywords)
    
    def _get_field_constraints(self, field_spec: Dict[str, Any]) -> List[str]:
        """Extract list of constraints for a field"""
        constraints = []
        
        if "minimum" in field_spec:
            constraints.append(f"min: {field_spec['minimum']}")
        if "maximum" in field_spec:
            constraints.append(f"max: {field_spec['maximum']}")
        if "minLength" in field_spec:
            constraints.append(f"minLength: {field_spec['minLength']}")
        if "maxLength" in field_spec:
            constraints.append(f"maxLength: {field_spec['maxLength']}")
        if "pattern" in field_spec:
            constraints.append(f"pattern: {field_spec['pattern']}")
        if "format" in field_spec:
            constraints.append(f"format: {field_spec['format']}")
        if "enum" in field_spec:
            constraints.append(f"enum: {len(field_spec['enum'])} values")
            
        return constraints
    
    def _determine_test_priority(self, field_name: str, field_spec: Dict[str, Any],
                                 schema: Dict[str, Any]) -> str:
        """
        Determine testing priority for a field
        
        Returns:
            Priority level: high, medium, or low
        """
        # High priority criteria
        if field_name in schema.get("required", []):
            return "high"
        
        if self._has_constraints(field_spec):
            return "high"
        
        # Check if it's likely a key field
        key_indicators = ["id", "key", "primary", "unique", "identifier"]
        if any(indicator in field_name.lower() for indicator in key_indicators):
            return "high"
        
        # Check if it's a business-critical field
        critical_indicators = ["amount", "price", "balance", "total", "status", "email"]
        if any(indicator in field_name.lower() for indicator in critical_indicators):
            return "high"
        
        # Medium priority for typed fields without constraints
        if field_spec.get("type") in self.supported_types:
            return "medium"
        
        return "low"
    
    def _extract_constraints(self, schema: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract all constraints from the schema
        
        Returns:
            Dictionary mapping constraint types to their occurrences
        """
        constraints = {
            "required_constraints": schema.get("required", []),
            "numeric_constraints": [],
            "string_constraints": [],
            "array_constraints": [],
            "custom_constraints": []
        }
        
        for field_name, field_spec in schema.get("properties", {}).items():
            field_type = field_spec.get("type", "unknown")
            
            if field_type in ["integer", "number"]:
                if "minimum" in field_spec or "maximum" in field_spec:
                    constraints["numeric_constraints"].append(field_name)
            elif field_type == "string":
                if any(k in field_spec for k in ["minLength", "maxLength", "pattern", "format"]):
                    constraints["string_constraints"].append(field_name)
            elif field_type == "array":
                if any(k in field_spec for k in ["minItems", "maxItems", "uniqueItems"]):
                    constraints["array_constraints"].append(field_name)
        
        return constraints
    
    def _calculate_complexity(self, schema: Dict[str, Any]) -> float:
        """
        Calculate schema complexity score (0-100)
        
        Higher scores indicate more complex schemas requiring more testing
        """
        score = 0
        
        # Base score from field count
        field_count = len(schema.get("properties", {}))
        score += min(field_count * 2, 30)  # Max 30 points
        
        # Required fields
        required_count = len(schema.get("required", []))
        score += min(required_count * 3, 20)  # Max 20 points
        
        # Nested objects
        nested_count = sum(
            1 for field_spec in schema.get("properties", {}).values()
            if field_spec.get("type") == "object"
        )
        score += min(nested_count * 5, 20)  # Max 20 points
        
        # Constraints
        total_constraints = sum(
            1 for field_spec in schema.get("properties", {}).values()
            if self._has_constraints(field_spec)
        )
        score += min(total_constraints * 3, 30)  # Max 30 points
        
        return min(score, 100)
    
    def _generate_test_recommendations(self, schema: Dict[str, Any]) -> List[str]:
        """
        Generate test recommendations based on schema analysis
        
        Returns:
            List of recommended test types
        """
        recommendations = []
        
        # Always recommend basic tests
        recommendations.append("Schema compliance validation")
        recommendations.append("Required field validation")
        recommendations.append("Data type validation")
        
        # Check for specific scenarios
        properties = schema.get("properties", {})
        
        # Numeric fields -> boundary tests
        numeric_fields = [
            name for name, spec in properties.items()
            if spec.get("type") in ["integer", "number"]
        ]
        if numeric_fields:
            recommendations.append(f"Boundary testing for numeric fields: {', '.join(numeric_fields[:3])}")
        
        # String patterns -> pattern validation
        pattern_fields = [
            name for name, spec in properties.items()
            if "pattern" in spec or "format" in spec
        ]
        if pattern_fields:
            recommendations.append(f"Pattern validation for: {', '.join(pattern_fields[:3])}")
        
        # Arrays -> collection tests
        array_fields = [
            name for name, spec in properties.items()
            if spec.get("type") == "array"
        ]
        if array_fields:
            recommendations.append(f"Collection validation for arrays: {', '.join(array_fields[:3])}")
        
        # Enum fields -> enum validation
        enum_fields = [
            name for name, spec in properties.items()
            if "enum" in spec
        ]
        if enum_fields:
            recommendations.append(f"Enum validation for: {', '.join(enum_fields[:3])}")
        
        # Complex schema -> integration tests
        if self._calculate_complexity(schema) > 50:
            recommendations.append("End-to-end integration tests for complex schema")
        
        return recommendations
    
    def compare_schemas(self, schema1: Dict[str, Any], 
                       schema2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two schemas to identify differences
        
        Args:
            schema1: First schema
            schema2: Second schema
            
        Returns:
            Comparison results showing additions, deletions, and modifications
        """
        fields1 = set(schema1.get("properties", {}).keys())
        fields2 = set(schema2.get("properties", {}).keys())
        
        comparison = {
            "added_fields": list(fields2 - fields1),
            "removed_fields": list(fields1 - fields2),
            "common_fields": list(fields1 & fields2),
            "modified_fields": [],
            "schema_version_change": schema1.get("version") != schema2.get("version")
        }
        
        # Check for modifications in common fields
        for field in comparison["common_fields"]:
            spec1 = schema1.get("properties", {}).get(field, {})
            spec2 = schema2.get("properties", {}).get(field, {})
            
            if spec1 != spec2:
                comparison["modified_fields"].append({
                    "field": field,
                    "old_spec": spec1,
                    "new_spec": spec2
                })
        
        # Check required fields changes
        required1 = set(schema1.get("required", []))
        required2 = set(schema2.get("required", []))
        
        comparison["required_changes"] = {
            "newly_required": list(required2 - required1),
            "no_longer_required": list(required1 - required2)
        }
        
        return comparison
    
    def validate_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that schema is well-formed
        
        Args:
            schema: Schema to validate
            
        Returns:
            Validation results
        """
        issues = []
        warnings = []
        
        # Check for required elements
        if "properties" not in schema:
            issues.append("Schema missing 'properties' field")
        
        # Check for empty schema
        if not schema.get("properties"):
            warnings.append("Schema has no properties defined")
        
        # Check field definitions
        for field_name, field_spec in schema.get("properties", {}).items():
            if "type" not in field_spec:
                warnings.append(f"Field '{field_name}' missing type definition")
            
            field_type = field_spec.get("type")
            if isinstance(field_type, str) and field_type not in self.supported_types:
                warnings.append(f"Field '{field_name}' has unsupported type: {field_type}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "validated_at": datetime.now().isoformat()
        }
