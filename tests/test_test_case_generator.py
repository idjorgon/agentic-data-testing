"""
Sample unit tests for the Test Case Generator
"""

import pytest
from src.core.test_case_generator import TestCaseGenerator


@pytest.fixture
def sample_schema():
    """Sample schema for testing"""
    return {
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "minimum": 0.01,
                "maximum": 1000.00
            },
            "status": {
                "type": "string",
                "enum": ["active", "inactive", "pending"]
            },
            "email": {
                "type": "string",
                "format": "email"
            }
        },
        "required": ["amount", "status"]
    }


def test_generator_initialization():
    """Test TestCaseGenerator initialization"""
    generator = TestCaseGenerator(seed=42)
    assert generator is not None


def test_generate_valid_data(sample_schema):
    """Test valid data generation"""
    generator = TestCaseGenerator(seed=42)
    data = generator.generate_valid_data(sample_schema, count=5)
    
    assert len(data) == 5
    for record in data:
        assert "amount" in record
        assert "status" in record
        assert record["status"] in ["active", "inactive", "pending"]


def test_generate_invalid_data(sample_schema):
    """Test invalid data generation"""
    generator = TestCaseGenerator(seed=42)
    data = generator.generate_invalid_data(sample_schema, violation_type="type")
    
    assert data is not None
    # Should have at least one field with wrong type


def test_generate_edge_cases(sample_schema):
    """Test edge case generation"""
    generator = TestCaseGenerator(seed=42)
    edge_cases = generator.generate_edge_cases(sample_schema)
    
    assert isinstance(edge_cases, list)
    assert len(edge_cases) > 0


def test_generate_valid_string():
    """Test string generation"""
    generator = TestCaseGenerator(seed=42)
    field_spec = {
        "type": "string",
        "minLength": 5,
        "maxLength": 20
    }
    
    value = generator._generate_valid_string("test_field", field_spec)
    assert isinstance(value, str)
    assert 5 <= len(value) <= 20


def test_generate_valid_integer():
    """Test integer generation"""
    generator = TestCaseGenerator(seed=42)
    field_spec = {
        "type": "integer",
        "minimum": 10,
        "maximum": 100
    }
    
    value = generator._generate_valid_integer(field_spec)
    assert isinstance(value, int)
    assert 10 <= value <= 100


def test_generate_email():
    """Test email generation"""
    generator = TestCaseGenerator(seed=42)
    email = generator._generate_email()
    
    assert isinstance(email, str)
    assert "@" in email
    assert "." in email


def test_generate_valid_array():
    """Test array generation"""
    generator = TestCaseGenerator(seed=42)
    field_spec = {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 2,
        "maxItems": 5
    }
    
    value = generator._generate_valid_array(field_spec)
    assert isinstance(value, list)
    assert 2 <= len(value) <= 5


def test_constraint_violation():
    """Test constraint violation generation"""
    generator = TestCaseGenerator(seed=42)
    field_spec = {
        "type": "number",
        "minimum": 10,
        "maximum": 100
    }
    
    value = generator._generate_constraint_violation(field_spec)
    # Should violate the constraint
    assert value is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
