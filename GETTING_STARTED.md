# 🚀 Getting Started - Run This Now!

## Immediate Next Steps

Your AI Agentic Data Testing MVP is ready! Here's what to do right now:

### 1️⃣ Install Dependencies (1 minute)

```bash
cd agentic-data-testing

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2️⃣ Set Up OpenAI API Key (30 seconds)

```bash
# Copy the template
cp .env.example .env

# Open .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

Or set it temporarily:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 3️⃣ Run Your First Demo (30 seconds)

```bash
# Option A: Run the financial validation demo (scripted)
python examples/demo_pipelines/chat_demo.py --mode scripted

# Option B: Try interactive chat mode
python examples/demo_pipelines/chat_demo.py --mode interactive
```

### 4️⃣ What You'll See

The demo will:
- ✅ Load the financial transaction schema
- ✅ Show AI-powered test planning
- ✅ Generate intelligent recommendations
- ✅ Demonstrate conversational interface

### 5️⃣ Try More Features

**Generate Test Cases:**
```python
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from agents import TestGeneratorAgent
from utils import load_json

generator = TestGeneratorAgent()
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")

test_suite = generator.generate_test_suite(schema)
print(f"\n✅ Generated {len(test_suite.test_cases)} test cases!")
print(f"📊 Coverage breakdown: {test_suite.coverage_summary}")
EOF
```

**Validate Data:**
```python
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from agents import ValidationAgent
from utils import load_json

validator = ValidationAgent()
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")
data = load_json("examples/sample_datasets/financial_transactions.json")

for i, record in enumerate(data[:3], 1):
    result = validator.validate_schema_compliance(record, schema)
    print(f"\n Transaction {i}: {result.overall_status.upper()}")
EOF
```

---

## 📚 Key Files to Explore

1. **[README.md](README.md)** - Complete documentation
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - What was built
3. **[docs/quick_start.md](docs/quick_start.md)** - Detailed tutorial
4. **[docs/architecture.md](docs/architecture.md)** - System design

---

## 🎯 What This MVP Can Do

✨ **AI Agents**
- Test Generator: Creates comprehensive test cases
- Validator: Validates data against schemas and business rules
- Orchestrator: Provides conversational interface

🔍 **Core Features**
- Schema analysis and insights
- Automated test case generation
- Boundary and edge case testing
- Synthetic data generation
- Data validation engine
- Regression testing
- Business rule validation
- Natural language test planning

📊 **Outputs**
- HTML test reports
- Markdown reports
- JSON results
- Conversational insights

---

## 💡 Example Use Cases

### Use Case 1: Validate Financial Transactions
```bash
python examples/demo_pipelines/financial_validation_demo.py
```

### Use Case 2: Chat About Testing Strategy
```bash
python examples/demo_pipelines/chat_demo.py --mode interactive
```
Then ask: "What tests should I create for high-value transactions?"

### Use Case 3: Generate Synthetic Test Data
```python
from agents import TestGeneratorAgent
from utils import load_json, save_json

generator = TestGeneratorAgent()
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")

# Generate 100 test records
data = generator.generate_synthetic_data(schema, count=100)
save_json(data, "my_test_data.json")
```

---

## 🐛 Troubleshooting

**"Module not found" error?**
→ Make sure you're in the project root and venv is activated

**"OpenAI API key not found"?**
→ Set it: `export OPENAI_API_KEY="sk-your-key"`

**Want to run without OpenAI?**
→ The core validation engine works without AI:
```python
from core import ValidationEngine, SchemaAnalyzer
# These work offline!
```

---

## 📞 Need Help?

- Check [docs/quick_start.md](docs/quick_start.md) for detailed guide
- See [examples/](examples/) for working code
- Read [README.md](README.md) for full documentation

---

## 🎉 You're Ready!

This MVP includes:
- ✅ 3 AI Agents (1,100+ lines)
- ✅ 3 Core Modules (1,300+ lines)
- ✅ Complete utilities & config
- ✅ Working demos
- ✅ Full documentation
- ✅ Unit tests
- ✅ Example data

**Start testing!** 🚀
