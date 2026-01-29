"""
Test Generator Agent
Analyzes data schemas and generates comprehensive test cases including boundary tests,
null checks, data type validations, and realistic synthetic data.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """Model for a generated test case"""
    test_name: str = Field(description="Name of the test case")
    test_type: str = Field(description="Type of test (boundary, null, type, business_rule, etc.)")
    description: str = Field(description="Description of what the test validates")
    test_data: Dict[str, Any] = Field(description="Sample data for the test")
    expected_outcome: str = Field(description="Expected outcome (pass/fail)")
    validation_rules: List[str] = Field(description="List of validation rules to apply")
    priority: str = Field(description="Test priority (high, medium, low)")


class TestSuite(BaseModel):
    """Model for a complete test suite"""
    suite_name: str = Field(description="Name of the test suite")
    test_cases: List[TestCase] = Field(description="List of test cases")
    coverage_summary: Dict[str, int] = Field(description="Summary of test coverage by type")
    

class TestGeneratorAgent:
    """
    AI Agent responsible for generating comprehensive test cases based on data schemas
    and business requirements.
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize the Test Generator Agent
        
        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature for LLM responses (0.0-1.0)
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.test_case_parser = PydanticOutputParser(pydantic_object=TestCase)
        self.test_suite_parser = PydanticOutputParser(pydantic_object=TestSuite)
        
    def analyze_schema(self, schema: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a data schema to understand structure and constraints
        
        Args:
            schema: Data schema dictionary
            context: Optional business context
            
        Returns:
            Analysis results with insights about the schema
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data testing analyst. Analyze the provided data schema 
            and identify key testing requirements including:
            - Data types and constraints
            - Required vs optional fields
            - Potential edge cases
            - Business logic implications
            - Data quality concerns"""),
            ("user", """Schema: {schema}
            
            Business Context: {context}
            
            Provide a comprehensive analysis of testing needs.""")
        ])
        
        chain = prompt_template | self.llm
        response = chain.invoke({
            "schema": json.dumps(schema, indent=2),
            "context": context or "No additional context provided"
        })
        
        return {
            "schema": schema,
            "analysis": response.content,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_boundary_tests(self, field_name: str, field_type: str, 
                               constraints: Optional[Dict] = None) -> List[TestCase]:
        """
        Generate boundary test cases for a specific field
        
        Args:
            field_name: Name of the field
            field_type: Data type of the field
            constraints: Optional constraints (min, max, pattern, etc.)
            
        Returns:
            List of boundary test cases
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating boundary test cases. 
            Create comprehensive boundary tests that check edge cases, limits, and extreme values."""),
            ("user", """Generate boundary test cases for:
            Field: {field_name}
            Type: {field_type}
            Constraints: {constraints}
            
            {format_instructions}""")
        ])
        
        test_cases = []
        
        # Generate tests based on field type
        if field_type in ["integer", "float", "decimal"]:
            min_val = constraints.get("minimum", 0) if constraints else 0
            max_val = constraints.get("maximum", 1000000) if constraints else 1000000
            
            test_cases.extend([
                TestCase(
                    test_name=f"{field_name}_minimum_boundary",
                    test_type="boundary",
                    description=f"Test minimum value for {field_name}",
                    test_data={field_name: min_val},
                    expected_outcome="pass",
                    validation_rules=[f"{field_name} >= {min_val}"],
                    priority="high"
                ),
                TestCase(
                    test_name=f"{field_name}_maximum_boundary",
                    test_type="boundary",
                    description=f"Test maximum value for {field_name}",
                    test_data={field_name: max_val},
                    expected_outcome="pass",
                    validation_rules=[f"{field_name} <= {max_val}"],
                    priority="high"
                ),
                TestCase(
                    test_name=f"{field_name}_below_minimum",
                    test_type="boundary",
                    description=f"Test below minimum value for {field_name}",
                    test_data={field_name: min_val - 1},
                    expected_outcome="fail",
                    validation_rules=[f"{field_name} >= {min_val}"],
                    priority="high"
                ),
                TestCase(
                    test_name=f"{field_name}_above_maximum",
                    test_type="boundary",
                    description=f"Test above maximum value for {field_name}",
                    test_data={field_name: max_val + 1},
                    expected_outcome="fail",
                    validation_rules=[f"{field_name} <= {max_val}"],
                    priority="high"
                )
            ])
            
        return test_cases
    
    def generate_null_tests(self, schema: Dict[str, Any]) -> List[TestCase]:
        """
        Generate null/missing value test cases
        
        Args:
            schema: Data schema dictionary
            
        Returns:
            List of null test cases
        """
        test_cases = []
        
        for field_name, field_spec in schema.get("properties", {}).items():
            required = field_name in schema.get("required", [])
            
            test_cases.append(
                TestCase(
                    test_name=f"{field_name}_null_test",
                    test_type="null_check",
                    description=f"Test null value handling for {field_name}",
                    test_data={field_name: None},
                    expected_outcome="fail" if required else "pass",
                    validation_rules=[f"{field_name} must not be null"] if required else [],
                    priority="high" if required else "medium"
                )
            )
            
            test_cases.append(
                TestCase(
                    test_name=f"{field_name}_missing_test",
                    test_type="null_check",
                    description=f"Test missing field handling for {field_name}",
                    test_data={},
                    expected_outcome="fail" if required else "pass",
                    validation_rules=[f"{field_name} must be present"] if required else [],
                    priority="high" if required else "medium"
                )
            )
            
        return test_cases
    
    def generate_type_tests(self, schema: Dict[str, Any]) -> List[TestCase]:
        """
        Generate data type validation test cases
        
        Args:
            schema: Data schema dictionary
            
        Returns:
            List of type validation test cases
        """
        test_cases = []
        
        type_mismatches = {
            "string": [123, True, [], {}],
            "integer": ["abc", 12.5, True, []],
            "number": ["abc", True, []],
            "boolean": ["true", 1, 0],
            "array": ["abc", 123, {}],
            "object": ["abc", 123, []]
        }
        
        for field_name, field_spec in schema.get("properties", {}).items():
            field_type = field_spec.get("type", "string")
            
            for wrong_value in type_mismatches.get(field_type, [])[:2]:  # Test 2 wrong types
                test_cases.append(
                    TestCase(
                        test_name=f"{field_name}_type_mismatch_{type(wrong_value).__name__}",
                        test_type="type_validation",
                        description=f"Test type validation for {field_name} with wrong type",
                        test_data={field_name: wrong_value},
                        expected_outcome="fail",
                        validation_rules=[f"{field_name} must be of type {field_type}"],
                        priority="high"
                    )
                )
                
        return test_cases
    
    def generate_synthetic_data(self, schema: Dict[str, Any], count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate realistic synthetic data based on schema
        
        Args:
            schema: Data schema dictionary
            count: Number of synthetic records to generate
            
        Returns:
            List of synthetic data records
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating realistic synthetic test data. 
            Create diverse, realistic data that covers normal cases and edge cases."""),
            ("user", """Generate {count} realistic data records based on this schema:
            
            {schema}
            
            Return as a JSON array of objects.""")
        ])
        
        chain = prompt_template | self.llm
        response = chain.invoke({
            "schema": json.dumps(schema, indent=2),
            "count": count
        })
        
        try:
            synthetic_data = json.loads(response.content)
            return synthetic_data if isinstance(synthetic_data, list) else [synthetic_data]
        except json.JSONDecodeError:
            # Fallback to basic synthetic data
            return self._generate_basic_synthetic_data(schema, count)
    
    def _generate_basic_synthetic_data(self, schema: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Generate basic synthetic data as fallback"""
        import random
        from faker import Faker
        
        fake = Faker()
        data = []
        
        for i in range(count):
            record = {}
            for field_name, field_spec in schema.get("properties", {}).items():
                field_type = field_spec.get("type", "string")
                
                if field_type == "string":
                    if "email" in field_name.lower():
                        record[field_name] = fake.email()
                    elif "name" in field_name.lower():
                        record[field_name] = fake.name()
                    elif "address" in field_name.lower():
                        record[field_name] = fake.address()
                    else:
                        record[field_name] = fake.word()
                elif field_type in ["integer", "number"]:
                    min_val = field_spec.get("minimum", 0)
                    max_val = field_spec.get("maximum", 1000)
                    record[field_name] = random.randint(min_val, max_val)
                elif field_type == "boolean":
                    record[field_name] = random.choice([True, False])
                    
            data.append(record)
            
        return data
    
    def generate_test_suite(self, schema: Dict[str, Any], 
                          business_context: Optional[str] = None) -> TestSuite:
        """
        Generate a comprehensive test suite for a given schema
        
        Args:
            schema: Data schema dictionary
            business_context: Optional business context
            
        Returns:
            Complete test suite
        """
        all_test_cases = []
        
        # Generate different types of tests
        all_test_cases.extend(self.generate_null_tests(schema))
        all_test_cases.extend(self.generate_type_tests(schema))
        
        # Generate boundary tests for numeric fields
        for field_name, field_spec in schema.get("properties", {}).items():
            field_type = field_spec.get("type", "string")
            if field_type in ["integer", "number"]:
                all_test_cases.extend(
                    self.generate_boundary_tests(field_name, field_type, field_spec)
                )
        
        # Calculate coverage summary
        coverage_summary = {}
        for test in all_test_cases:
            coverage_summary[test.test_type] = coverage_summary.get(test.test_type, 0) + 1
        
        return TestSuite(
            suite_name=f"Test Suite for {schema.get('title', 'Schema')}",
            test_cases=all_test_cases,
            coverage_summary=coverage_summary
        )
    
    def explain_test_results(self, test_results: List[Dict[str, Any]]) -> str:
        """
        Provide natural language explanation of test results
        
        Args:
            test_results: List of test execution results
            
        Returns:
            Natural language explanation
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data quality analyst. Explain test results in clear,
            business-friendly language. Highlight issues, patterns, and recommendations."""),
            ("user", """Analyze these test results and provide insights:
            
            {results}
            
            Provide:
            1. Summary of pass/fail rates
            2. Critical issues found
            3. Patterns in failures
            4. Recommendations for improvement""")
        ])
        
        chain = prompt_template | self.llm
        response = chain.invoke({
            "results": json.dumps(test_results, indent=2)
        })
        
        return response.content
