# Quick Start Guide

Get up and running with the AI Agentic Data Testing Framework in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key

## Step 1: Installation

```bash
# Clone the repository
git clone <repository-url>
cd agentic-data-testing

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-api-key-here
```

## Step 3: Run Your First Demo

```bash
# Run the financial validation demo
python examples/demo_pipelines/financial_validation_demo.py
```

You should see output like:
```
================================================================================
Starting Financial Transaction Validation Pipeline
================================================================================
Loading schema from: examples/sample_schemas/financial_transaction_schema.json
Loading data from: examples/sample_datasets/financial_transactions.json
Loaded 10 transactions
...
✨ Financial validation pipeline completed successfully!
```

## Step 4: Try Interactive Mode

```bash
python examples/demo_pipelines/chat_demo.py --mode interactive
```

Try asking questions like:
- "What tests should I create for this schema?"
- "How can I validate transaction amounts?"
- "What edge cases should I test?"

## Step 5: Use in Your Own Code

Create a new Python file:

```python
from src.agents import OrchestratorAgent
from src.utils import load_json

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Load your schema
schema = load_json("path/to/your/schema.json")

# Chat with the agent
response = orchestrator.chat(
    "Create a test plan for this schema",
    context={"schema": schema}
)

print(response)
```

## Common Tasks

### Generate Test Cases

```python
from src.agents import TestGeneratorAgent
from src.utils import load_json

generator = TestGeneratorAgent()
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")

# Generate complete test suite
test_suite = generator.generate_test_suite(schema)

print(f"Generated {len(test_suite.test_cases)} test cases")
print(f"Coverage: {test_suite.coverage_summary}")
```

### Validate Data

```python
from src.agents import ValidationAgent
from src.utils import load_json

validator = ValidationAgent()
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")
data = load_json("examples/sample_datasets/financial_transactions.json")

# Validate each record
for record in data:
    result = validator.validate_schema_compliance(record, schema)
    if result.overall_status == "failed":
        print(f"Validation failed: {result.errors}")
```

### Generate Synthetic Data

```python
from src.agents import TestGeneratorAgent
from src.utils import load_json, save_json

generator = TestGeneratorAgent()
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")

# Generate 100 synthetic records
synthetic_data = generator.generate_synthetic_data(schema, count=100)

# Save to file
save_json(synthetic_data, "output/synthetic_transactions.json")
```

### Create Test Reports

```python
from src.utils import ReportGenerator
from src.config import Config

# Your test results
results = {
    "total_tests": 50,
    "passed": 45,
    "failed": 5,
    "pass_rate": 90.0,
    "test_results": [...]
}

# Generate HTML report
ReportGenerator.generate_html_report(
    results,
    f"{Config.REPORTS_DIR}/test_report.html"
)
```

## Next Steps

1. **Explore Examples** - Check out `examples/demo_pipelines/` for more examples
2. **Read Documentation** - See `docs/architecture.md` for system design
3. **Customize** - Edit `src/config/settings.py` to customize behavior
4. **Extend** - Add your own custom validators and test generators
5. **Integrate** - Connect with your existing data pipelines

## Troubleshooting

### "OpenAI API key not found"
- Make sure you've created `.env` file from `.env.example`
- Verify your API key is correctly set in `.env`
- Check that `.env` is in the project root directory

### "Module not found"
- Ensure you've activated the virtual environment
- Run `pip install -r requirements.txt` again
- Check Python version with `python --version` (should be 3.8+)

### "ImportError" when running demos
- Make sure you're running from the project root directory
- The demos add `src` to the Python path automatically

## Getting Help

- **Documentation**: Check the `docs/` folder
- **Examples**: See `examples/` for working code
- **Issues**: Report bugs on GitHub Issues
- **Questions**: Use GitHub Discussions

## What's Next?

Try these advanced features:
- Regression testing with baseline comparisons
- Custom business rule validation
- Integration with your CI/CD pipeline
- Building custom agents for domain-specific testing

Happy Testing! 🚀
