"""
Test Case Generator
Generates various types of test cases based on schemas, constraints, and business rules.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import string


class TestCaseGenerator:
    """
    Generates test cases and test data for comprehensive data testing.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the Test Case Generator
        
        Args:
            seed: Random seed for reproducible test generation
        """
        if seed is not None:
            random.seed(seed)
        
    def generate_valid_data(self, schema: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        """
        Generate valid test data that conforms to schema
        
        Args:
            schema: Data schema
            count: Number of valid records to generate
            
        Returns:
            List of valid data records
        """
        data = []
        
        for i in range(count):
            record = {}
            for field_name, field_spec in schema.get("properties", {}).items():
                record[field_name] = self._generate_valid_value(field_name, field_spec)
            data.append(record)
        
        return data
    
    def generate_invalid_data(self, schema: Dict[str, Any], 
                             violation_type: str = "type") -> Dict[str, Any]:
        """
        Generate invalid test data that violates schema
        
        Args:
            schema: Data schema
            violation_type: Type of violation (type, required, constraint, etc.)
            
        Returns:
            Invalid data record
        """
        record = {}
        violated = False
        
        for field_name, field_spec in schema.get("properties", {}).items():
            if not violated and random.random() < 0.3:  # 30% chance to violate this field
                if violation_type == "type":
                    record[field_name] = self._generate_wrong_type_value(field_spec)
                elif violation_type == "constraint":
                    record[field_name] = self._generate_constraint_violation(field_spec)
                elif violation_type == "required" and field_name in schema.get("required", []):
                    # Skip required field
                    continue
                else:
                    record[field_name] = self._generate_valid_value(field_name, field_spec)
                violated = True
            else:
                record[field_name] = self._generate_valid_value(field_name, field_spec)
        
        return record
    
    def generate_edge_cases(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate edge case test data
        
        Args:
            schema: Data schema
            
        Returns:
            List of edge case records
        """
        edge_cases = []
        
        for field_name, field_spec in schema.get("properties", {}).items():
            field_type = field_spec.get("type", "string")
            
            if field_type in ["integer", "number"]:
                # Numeric edge cases
                edge_cases.extend(self._generate_numeric_edge_cases(field_name, field_spec, schema))
            elif field_type == "string":
                # String edge cases
                edge_cases.extend(self._generate_string_edge_cases(field_name, field_spec, schema))
            elif field_type == "array":
                # Array edge cases
                edge_cases.extend(self._generate_array_edge_cases(field_name, field_spec, schema))
        
        return edge_cases
    
    def _generate_valid_value(self, field_name: str, field_spec: Dict[str, Any]) -> Any:
        """Generate a valid value for a field"""
        field_type = field_spec.get("type", "string")
        
        # Check for enum first
        if "enum" in field_spec:
            return random.choice(field_spec["enum"])
        
        if field_type == "string":
            return self._generate_valid_string(field_name, field_spec)
        elif field_type == "integer":
            return self._generate_valid_integer(field_spec)
        elif field_type == "number":
            return self._generate_valid_number(field_spec)
        elif field_type == "boolean":
            return random.choice([True, False])
        elif field_type == "array":
            return self._generate_valid_array(field_spec)
        elif field_type == "object":
            return {}
        else:
            return None
    
    def _generate_valid_string(self, field_name: str, field_spec: Dict[str, Any]) -> str:
        """Generate valid string value"""
        min_length = field_spec.get("minLength", 1)
        max_length = field_spec.get("maxLength", 50)
        format_type = field_spec.get("format")
        
        # Handle specific formats
        if format_type == "email":
            return self._generate_email()
        elif format_type == "date":
            return datetime.now().date().isoformat()
        elif format_type == "date-time":
            return datetime.now().isoformat()
        elif format_type == "uri":
            return "https://example.com/resource"
        elif format_type == "uuid":
            import uuid
            return str(uuid.uuid4())
        
        # Handle pattern
        if "pattern" in field_spec:
            # Simple pattern matching for common cases
            pattern = field_spec["pattern"]
            if pattern == "^[0-9]+$":
                return "".join(random.choices(string.digits, k=random.randint(min_length, max_length)))
            elif pattern == "^[A-Z]+$":
                return "".join(random.choices(string.ascii_uppercase, k=random.randint(min_length, max_length)))
        
        # Generate based on field name hints
        if "name" in field_name.lower():
            return random.choice(["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams"])
        elif "email" in field_name.lower():
            return self._generate_email()
        elif "phone" in field_name.lower():
            return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
        elif "address" in field_name.lower():
            return f"{random.randint(1, 9999)} Main St, City, ST {random.randint(10000, 99999)}"
        elif "city" in field_name.lower():
            return random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])
        elif "state" in field_name.lower():
            return random.choice(["CA", "NY", "TX", "FL", "IL"])
        
        # Default: random string
        length = random.randint(min_length, min(max_length, 20))
        return "".join(random.choices(string.ascii_letters + " ", k=length))
    
    def _generate_valid_integer(self, field_spec: Dict[str, Any]) -> int:
        """Generate valid integer value"""
        minimum = field_spec.get("minimum", 0)
        maximum = field_spec.get("maximum", 1000000)
        multiple_of = field_spec.get("multipleOf")
        
        if multiple_of:
            # Generate multiple of specified value
            multiplier = random.randint(minimum // multiple_of, maximum // multiple_of)
            return multiplier * multiple_of
        
        return random.randint(minimum, maximum)
    
    def _generate_valid_number(self, field_spec: Dict[str, Any]) -> float:
        """Generate valid number (float) value"""
        minimum = field_spec.get("minimum", 0.0)
        maximum = field_spec.get("maximum", 1000000.0)
        
        return round(random.uniform(minimum, maximum), 2)
    
    def _generate_valid_array(self, field_spec: Dict[str, Any]) -> List[Any]:
        """Generate valid array value"""
        min_items = field_spec.get("minItems", 0)
        max_items = field_spec.get("maxItems", 10)
        items_spec = field_spec.get("items", {"type": "string"})
        
        count = random.randint(min_items, max_items)
        return [self._generate_valid_value("item", items_spec) for _ in range(count)]
    
    def _generate_email(self) -> str:
        """Generate random email address"""
        domains = ["example.com", "test.com", "demo.org", "sample.net"]
        username = "".join(random.choices(string.ascii_lowercase, k=8))
        return f"{username}@{random.choice(domains)}"
    
    def _generate_wrong_type_value(self, field_spec: Dict[str, Any]) -> Any:
        """Generate value of wrong type"""
        field_type = field_spec.get("type", "string")
        
        wrong_types = {
            "string": [123, True, [], {}],
            "integer": ["abc", 12.5, True, []],
            "number": ["abc", True, []],
            "boolean": ["true", 1, []],
            "array": ["abc", 123, {}],
            "object": ["abc", 123, []]
        }
        
        candidates = wrong_types.get(field_type, ["invalid"])
        return random.choice(candidates)
    
    def _generate_constraint_violation(self, field_spec: Dict[str, Any]) -> Any:
        """Generate value that violates constraints"""
        field_type = field_spec.get("type", "string")
        
        if field_type in ["integer", "number"]:
            if "minimum" in field_spec:
                return field_spec["minimum"] - 1
            elif "maximum" in field_spec:
                return field_spec["maximum"] + 1
        elif field_type == "string":
            if "minLength" in field_spec and field_spec["minLength"] > 0:
                return ""
            elif "maxLength" in field_spec:
                return "x" * (field_spec["maxLength"] + 10)
        elif field_type == "array":
            if "minItems" in field_spec and field_spec["minItems"] > 0:
                return []
            elif "maxItems" in field_spec:
                return [1] * (field_spec["maxItems"] + 5)
        
        return None
    
    def _generate_numeric_edge_cases(self, field_name: str, field_spec: Dict[str, Any],
                                    schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate numeric edge cases"""
        edge_cases = []
        minimum = field_spec.get("minimum", 0)
        maximum = field_spec.get("maximum", 1000000)
        
        # Minimum boundary
        case = {field_name: minimum}
        for other_field, other_spec in schema.get("properties", {}).items():
            if other_field != field_name:
                case[other_field] = self._generate_valid_value(other_field, other_spec)
        edge_cases.append(case)
        
        # Maximum boundary
        case = {field_name: maximum}
        for other_field, other_spec in schema.get("properties", {}).items():
            if other_field != field_name:
                case[other_field] = self._generate_valid_value(other_field, other_spec)
        edge_cases.append(case)
        
        # Zero
        if minimum <= 0 <= maximum:
            case = {field_name: 0}
            for other_field, other_spec in schema.get("properties", {}).items():
                if other_field != field_name:
                    case[other_field] = self._generate_valid_value(other_field, other_spec)
            edge_cases.append(case)
        
        return edge_cases
    
    def _generate_string_edge_cases(self, field_name: str, field_spec: Dict[str, Any],
                                   schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate string edge cases"""
        edge_cases = []
        
        # Empty string
        if field_spec.get("minLength", 0) == 0:
            case = {field_name: ""}
            for other_field, other_spec in schema.get("properties", {}).items():
                if other_field != field_name:
                    case[other_field] = self._generate_valid_value(other_field, other_spec)
            edge_cases.append(case)
        
        # Maximum length string
        if "maxLength" in field_spec:
            case = {field_name: "x" * field_spec["maxLength"]}
            for other_field, other_spec in schema.get("properties", {}).items():
                if other_field != field_name:
                    case[other_field] = self._generate_valid_value(other_field, other_spec)
            edge_cases.append(case)
        
        # Special characters
        case = {field_name: "!@#$%^&*()"}
        for other_field, other_spec in schema.get("properties", {}).items():
            if other_field != field_name:
                case[other_field] = self._generate_valid_value(other_field, other_spec)
        edge_cases.append(case)
        
        return edge_cases
    
    def _generate_array_edge_cases(self, field_name: str, field_spec: Dict[str, Any],
                                  schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate array edge cases"""
        edge_cases = []
        
        # Empty array
        if field_spec.get("minItems", 0) == 0:
            case = {field_name: []}
            for other_field, other_spec in schema.get("properties", {}).items():
                if other_field != field_name:
                    case[other_field] = self._generate_valid_value(other_field, other_spec)
            edge_cases.append(case)
        
        # Single item
        items_spec = field_spec.get("items", {"type": "string"})
        case = {field_name: [self._generate_valid_value("item", items_spec)]}
        for other_field, other_spec in schema.get("properties", {}).items():
            if other_field != field_name:
                case[other_field] = self._generate_valid_value(other_field, other_spec)
        edge_cases.append(case)
        
        return edge_cases
