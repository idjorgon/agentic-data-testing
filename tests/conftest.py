"""
Test configuration and fixtures
"""

import pytest


@pytest.fixture
def simple_schema():
    """Simple schema for basic testing"""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id"]
    }


@pytest.fixture
def complex_schema():
    """Complex schema for advanced testing"""
    return {
        "type": "object",
        "properties": {
            "transaction_id": {
                "type": "string",
                "pattern": "^TXN[0-9]{10}$"
            },
            "amount": {
                "type": "number",
                "minimum": 0.01,
                "maximum": 1000000.00
            },
            "currency": {
                "type": "string",
                "enum": ["USD", "EUR", "GBP"]
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 0,
                "maxItems": 10
            }
        },
        "required": ["transaction_id", "amount", "currency"]
    }


@pytest.fixture
def sample_data():
    """Sample valid data"""
    return [
        {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        },
        {
            "id": 2,
            "name": "Another User",
            "email": "another@example.com"
        }
    ]
