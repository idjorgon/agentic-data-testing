"""
Sample unit tests for the Schema Analyzer
"""

import copy
import pytest
from src.core.schema_analyzer import SchemaAnalyzer


@pytest.fixture
def sample_schema():
    """Sample schema for testing"""
    return {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "minimum": 1
            },
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 150
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "minItems": 0,
                "maxItems": 10
            }
        },
        "required": ["id", "name", "email"]
    }


def test_schema_analyzer_initialization():
    """Test SchemaAnalyzer initialization"""
    analyzer = SchemaAnalyzer()
    assert analyzer is not None
    assert len(analyzer.supported_types) > 0


def test_analyze_schema(sample_schema):
    """Test schema analysis"""
    analyzer = SchemaAnalyzer()
    result = analyzer.analyze(sample_schema)
    
    assert result is not None
    assert "field_count" in result
    assert result["field_count"] == 5
    assert "required_fields" in result
    assert len(result["required_fields"]) == 3
    assert "id" in result["required_fields"]


def test_detect_schema_type(sample_schema):
    """Test schema type detection"""
    analyzer = SchemaAnalyzer()
    schema_type = analyzer._detect_schema_type(sample_schema)
    assert schema_type == "custom"
    
    json_schema = {**sample_schema, "$schema": "http://json-schema.org/draft-07/schema#"}
    schema_type = analyzer._detect_schema_type(json_schema)
    assert schema_type == "json_schema"


def test_calculate_complexity(sample_schema):
    """Test complexity calculation"""
    analyzer = SchemaAnalyzer()
    complexity = analyzer._calculate_complexity(sample_schema)
    assert isinstance(complexity, (int, float))
    assert 0 <= complexity <= 100


def test_validate_schema(sample_schema):
    """Test schema validation"""
    analyzer = SchemaAnalyzer()
    result = analyzer.validate_schema(sample_schema)
    
    assert result["valid"] == True
    assert isinstance(result["issues"], list)
    assert isinstance(result["warnings"], list)


def test_compare_schemas(sample_schema):
    """Test schema comparison"""
    analyzer = SchemaAnalyzer()
    
    # Create a modified schema (deep copy to avoid modifying the original)
    modified_schema = copy.deepcopy(sample_schema)
    modified_schema["properties"]["new_field"] = {"type": "string"}
    
    comparison = analyzer.compare_schemas(sample_schema, modified_schema)
    
    assert "added_fields" in comparison
    assert "new_field" in comparison["added_fields"]
    assert "removed_fields" in comparison
    assert "modified_fields" in comparison


def test_field_analysis(sample_schema):
    """Test field analysis"""
    analyzer = SchemaAnalyzer()
    analysis = analyzer.analyze(sample_schema)
    
    field_analysis = analysis["field_analysis"]
    assert "name" in field_analysis
    assert field_analysis["name"]["type"] == "string"
    assert field_analysis["name"]["required"] == True


def test_constraint_extraction(sample_schema):
    """Test constraint extraction"""
    analyzer = SchemaAnalyzer()
    analysis = analyzer.analyze(sample_schema)
    
    constraints = analysis["constraints"]
    assert "required_constraints" in constraints
    assert "numeric_constraints" in constraints
    assert "string_constraints" in constraints


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
