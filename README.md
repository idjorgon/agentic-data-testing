# AI Agentic Data Testing Framework

<div align="center">

🤖 **Intelligent Test Case Generation & Validation MVP**

*AI-powered testing solution for data pipelines with conversational interface*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🎯 Overview

The AI Agentic Data Testing Framework is an intelligent, AI-powered solution that automatically generates comprehensive test cases and validates data transformations in data pipelines. It leverages Large Language Models (LLMs) to provide schema-aware test generation, intelligent edge case discovery, and context-aware validation with a natural language conversational interface.

### Key Features

✨ **Schema-Aware Test Generation** - Automatically generates comprehensive test cases based on data contracts and schemas

🔍 **Intelligent Edge Case Discovery** - AI-powered identification and generation of boundary conditions and edge cases

🤖 **Automated Regression Testing** - Detects regressions when pipeline changes occur

🎯 **Context-Aware Validation** - Adapts validation rules to business logic and domain requirements

💬 **Conversational Interface** - Natural language interaction for test planning and results interpretation

📊 **Comprehensive Reporting** - Generate HTML, Markdown, and JSON reports with actionable insights

---

## 🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        USER[👤 User/Developer]
        CHAT[💬 Chat Interface]
        CLI[⌨️ CLI/Scripts]
    end
    
    subgraph "Orchestration Layer"
        ORCH[🎯 Orchestrator Agent]
    end
    
    subgraph "AI Agent Layer"
        TESTGEN[🤖 Test Generator Agent<br/>- Analyze schemas<br/>- Generate test cases<br/>- Create synthetic data]
        VALID[✅ Validation Agent<br/>- Schema compliance<br/>- Business rules<br/>- Regression testing]
        PROFILER[📊 Data Profiler<br/>- Column profiling<br/>- Anomaly detection<br/>- Drift detection]
        MONITOR[📈 Monitoring Agent<br/>- Track metrics<br/>- Threshold alerts<br/>- Trend analysis]
    end
    
    subgraph "Core Processing Layer"
        SCHEMA[📋 Schema Analyzer]
        TESTCASE[🔨 Test Case Generator]
        ENGINE[⚙️ Validation Engine]
    end
    
    subgraph "Data & Storage Layer"
        DATASETS[(📁 Sample Datasets)]
        SCHEMAS[(📄 Schemas)]
        REPORTS[(📊 Reports)]
        BASELINE[(💾 Baseline Profiles)]
    end
    
    subgraph "External Services"
        GPT4[🧠 OpenAI GPT-4]
    end
    
    subgraph "Utilities"
        LOGGER[📝 Logger]
        DATAUTILS[🔧 Data Utils<br/>- Secure file ops<br/>- Path validation]
        REPORTGEN[📄 Report Generator<br/>- HTML/MD/JSON]
    end
    
    %% User interactions
    USER -->|Natural Language| CHAT
    USER -->|Execute| CLI
    CHAT --> ORCH
    CLI --> ORCH
    
    %% Orchestrator coordinates agents
    ORCH -->|Plan & Execute| TESTGEN
    ORCH -->|Validate| VALID
    ORCH -->|Track & Alert| MONITOR
    
    %% Agent interactions with core
    TESTGEN --> SCHEMA
    TESTGEN --> TESTCASE
    VALID --> ENGINE
    PROFILER -->|Statistical Analysis| DATASETS
    MONITOR -->|Metrics from| PROFILER
    MONITOR -->|Check Threshold
    PROFILER -->|Statistical Analysis| DATASETS
    
    %% Core processing
    SCHEMA --> SCHEMAS
    TESTCASE --> DATASETS
    ENGINE --> DATASETS
    
    %% AI Integration
    TESTGEN -.->|API Calls| GPT4
    VALID -.->|API Calls| GPT4
    ORCH -.->|Chat| GPT4
    
    MONITOR -->|Alerts| REPORTGEN
    %% Data flow
    PROFILER --> BASELINE
    PROFILER -->|Anomalies| REPORTGEN
    ENGINE -->|Results| REPORTGEN
    REPORTGEN --> REPORTS
    
    MONITOR --> LOGGER
    ORCH --> DATAUTILS
    PROFILER --> DATAUTILS
    MONITOR --> DATAUTILS
    
    %% Styling
    classDef agentClass fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef coreClass fill:#2196F3,stroke:#1565C0,color:#fff
    classDef dataClass fill:#FF9800,stroke:#E65100,color:#fff
    classDef utilClass fill:#9E9E9E,stroke:#424242,color:#fff
    classDef extClass fill:#9C27B0,stroke:#6A1B9A,color:#fff
    
    class TESTGEN,VALID,PROFILER,ORCH,MONITORtroke:#E65100,color:#fff
    classDef utilClass fill:#9E9E9E,stroke:#424242,color:#fff
    classDef extClass fill:#9C27B0,stroke:#6A1B9A,color:#fff
    
    class TESTGEN,VALID,PROFILER,ORCH agentClass
    class SCHEMA,TESTCASE,ENGINE coreClass
    class DATASETS,SCHEMAS,REPORTS,BASELINE dataClass
    class LOGGER,DATAUTILS,REPORTGEN utilClass
    class GPT4 extClass
```

### Agentic WorkMonitor as Monitoring Agent
    participant Profiler
    participant TestGen as Test Generator
    participant Validator
    participant GPT4 as OpenAI GPT-4
    participant Reports
    
    User->>Orchestrator: Submit schema + data + business rules
    
    Note over Orchestrator: Step 1: Data Profiling
    Orchestrator->>Profiler: Profile dataset
    Profiler->>Profiler: Analyze columns (types, nulls, distributions)
    Profiler->>Profiler: Detect anomalies (IQR/Z-score)
    Profiler->>Profiler: Check for drift vs baseline
    Profiler-->>Orchestrator: Profile results + anomalies
    
    Note over Orchestrator: Step 1b: Continuous Monitoring
    Orchestrator->>Monitor: Track profiling metrics
    Monitor->>Monitor: Record metric snapshots
    Monitor->>Monitor: Check thresholds
    Monitor->>Monitor: Detect trends
    Monitor-->>Orchestrator: Alerts (if any)
    
    alt Critical Alerts Triggered
        Monitor-->>User: 🚨 Alert notifications
        Note over User: Review alerts:<br/>- High null percentages<br/>- Anomaly spikes<br/>- Data drift detected
    end
    
    Note over Orchestrator: Step 2: Test Generation (Optional)
    Orchestrator->>TestGen: Analyze schema
    TestGen->>GPT4: Request schema analysis
    GPT4-->>TestGen: Analysis & insights
    TestGen->>GPT4: Generate test cases
    GPT4-->>TestGen: Comprehensive test suite
    TestGen-->>Orchestrator: Test cases + synthetic data
    
    Note over Orchestrator: Step 3: Validation
    Orchestrator->>Validator: Validate data
    Validator->>Validator: Check schema compliance
    Validator->>Validator: Validate business rules
    Validator->>GPT4: Request AI-powered validation
    GPT4-->>Validator: Validation insights
    Validator-->>Orchestrator: Validation results
    
    Note over Orchestrator: Step 4: Reporting
    Orchestrator->>Reports: Generate reports
    Reports->>Reports: Create HTML report
    Reports->>Reports: Create Markdown report
    Reports->>Reports: Create JSON report
    Monitor->>Reports: Include monitoring metrics
    Reports-->>Orchestrator: Report files
    
    Orchestrator-->>User: Complete results + recommendations
    
    Note├── orchestrator_agent.py      # Coordinates workflows
│   │   └── monitoring_agent.py        # 🆕 Continuous monitoring & alerting
│   ├── core/                      # Core testing engine
│   │   ├── schema_analyzer.py         # Schema analysis & insights
│   │   ├── test_case_generator.py     # Test data generation
│   │   ├── validation_engine.py       # Validation execution
│   │   └── data_profiler.py           # Data profiling & drift detection
│   ├── utils/                     # Utilities
│   │   ├── logger.py
│   │   ├── data_utils.py
│   │   └── report_generator.py
│   └── config/                    # Configuration
│       └── settings.py
├── examples/                      # Example data & demos
│   ├── sample_datasets/
│   ├── sample_schemas/
│   └── demo_pipelines/
│       ├── chat_demo.py
│       ├── financial_validation_demo.py
│       └── monitoring_demo.py         # 🆕 Monitoring simulationtor_agent.py    # Generates test cases
│   │   ├── validation_agent.py        # Validates data & pipelines
│   │   └── orchestrator_agent.py      # Coordinates workflows
│   ├── core/                      # Core testing engine
│   │   ├── schema_analyzer.py         # Schema analysis & insights
│   │   ├── test_case_generator.py     # Test data generation
│   │   ├── validation_engine.py       # Validation execution
│   │   └── data_profiler.py           # 🆕 Data profiling & drift detection
│   ├── utils/                     # Utilities
│   │   ├── logger.py
│   │   ├── data_utils.py
│   │   └── report_generator.py
│   └── config/                    # Configuration
│       └── settings.py
├── examples/                      # Example data & demos
│   ├── sample_datasets/
│   ├── sample_schemas/
│   └── demo_pipelines/
├── tests/                         # Unit tests
├── docs/                          # Documentation
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for GPT-4)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd agentic-data-testing
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Run Your First Demo

```bash
# Run the financial validation demo (with profiling & mocked validation)
python examples/demo_pipelines/financial_validation_demo.py

# Try the interactive chat interface
python examples/demo_pipelines/chat_demo.py --mode interactive

# 🆕 Run monitoring simulation (NO API calls - pure analytics!)
python examples/demo_pipelines/monitoring_demo.py
```

---

## 💡 Core Components

### 1. Test Generator Agent

Analyzes data schemas and generates comprehensive test cases.

```python
from agents import TestGeneratorAgent

generator = TestGeneratorAgent()

# Analyze schema
analysis = generator.analyze_schema(schema, context="Financial transactions")

# Generate test suite
test_suite = generator.generate_test_suite(schema)

# Generate synthetic data
synthetic_data = generator.generate_synthetic_data(schema, count=100)
```

**Capabilities:**
- Boundary testing for numeric fields
- Null/missing value tests
- Data type validation tests
- Pattern and format validation
- Synthetic data generation
- Edge case discovery

### 2. Validation Agent

Monitors data transformations and validates business logic.

```python
from agents import ValidationAgent

validator = ValidationAgent()

# Validate schema compliance
result = validator.validate_schema_compliance(data, schema)

# Validate business rules
business_rules = [
    {
        "name": "amount_positive",
        "type": "range",
        "field": "amount",
        "min": 0.01,
        "max": 1000000
    }
]
validations = validator.validate_business_rules(data, business_rules)

# Perform regression testing
regression_report = validator.perform_regression_test(
    baseline_results, 
    current_results
)
```

**Capabilities:**
- Schema compliance validation
- Business rule validation
- Transformation verification
- Regression detection
- Data quality monitoring

### 3. Orchestrator Agent

Coordinates testing workflows with conversational interface.

```python
from agents import OrchestratorAgent

orchestrator = OrchestratorAgent()

# Chat interface
response = orchestrator.chat(
    "What tests should I create for this schema?",
    context={"schema": schema}
)

# Execute complete workflow
results = orchestrator.execute_test_workflow(
    schema=schema,
    test_data=data,
    business_rules=rules
)

# Interpret results
interpretation = orchestrator.interpret_results(results)
```

**Capabilities:**
- Natural language test planning
- Workflow orchestration
- Multi-agent coordination
- Results interpretation
- Test improvement suggestions
- Continuous monitoring integration

### 4. Monitoring Agent 🆕

Tracks data quality metrics over time with automated alerting (NO API calls required).

```python
from agents import MonitoringAgent
from core import DataProfiler

# Initialize monitoring
monitor = MonitoringAgent(alert_config={
    "null_percentage_threshold": 10.0,
    "anomaly_count_threshold": 5,
    "alert_channels": ["log", "slack"]
})

# Profile dataset
profiler = DataProfiler()
profile = profiler.profile_dataset(data, "transactions")

# Track metrics
metrics = monitor.track_profiling_metrics(profile, "transactions")

# Check for alerts
alerts = monitor.check_thresholds(metrics)

if alerts:
    for alert in alerts:
        print(f"⚠️ {alert.severity}: {alert.message}")
        for rec in alert.recommendations:
            print(f"  • {rec}")

# Generate monitoring report
report = monitor.generate_monitoring_report()
print(f"Tracking {report['metrics_tracked']} metrics")
print(f"Active alerts: {report['active_alerts']}")
```

**Capabilities:**
- Metric tracking over time (in-memory & exportable)
- Threshold-based alerting (null %, anomalies, drift)
- Trend detection (increasing/decreasing/stable)
- Rate limiting (prevent alert fatigue)
- Historical analysis with volatility metrics
- Secure: Input validation, memory limits, sanitization
- NO OpenAI API required - pure Python analytics

**Security Features:**
- Input validation and sanitization
- Memory limits (10K metrics, 1K alerts)
- Path validation for file operations
- Rate limiting for alerts (prevent spam)
- Metric name sanitization
- Safe value checks (no NaN/Infinity)

---

## 📋 Usage Examples

### Example 1: Generate Test Cases for Financial Data

```python
from utils import load_json
from agents import TestGeneratorAgent

# Load schema
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")

# Create agent
generator = TestGeneratorAgent()

# Generate comprehensive test suite
test_suite = generator.generate_test_suite(schema)

print(f"Generated {len(test_suite.test_cases)} test cases")
print(f"Coverage: {test_suite.coverage_summary}")
```

### Example 2: Validate Data Pipeline

```python
from utils import load_json
from agents import ValidationAgent

# Load data
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")
data = load_json("examples/sample_datasets/financial_transactions.json")

# Validate
validator = ValidationAgent()

for record in data:
    result = validator.validate_schema_compliance(record, schema)
    if result.overall_status == "failed":
        print(f"Validation failed: {result.errors}")
```

### Example 3: Interactive Test Planning

```python
from agents import OrchestratorAgent
from utils import load_json

orchestrator = OrchestratorAgent()
schema = load_json("examples/sample_schemas/financial_transaction_schema.json")

# Have a conversation about testing
questions = [
    "What are the critical test areas for this schema?",
    "How should I test high-value transactions?",
    "What edge cases should I consider?"
]

for question in questions:
    response = orchestrator.chat(question, context={"schema": schema})
    print(f"Q: {question}")
    print(f"A: {response}\n")
```

### Example 4: Continuous Monitoring (No API!) 🆕

```python
from agents import MonitoringAgent
from core import DataProfiler
from utils import load_json

# Initialize
profiler = DataProfiler()
monitor = MonitoringAgent(alert_config={
    "null_percentage_threshold": 10.0,
    "anomaly_count_threshold": 5
})

# Simulate daily monitoring
for day in range(1, 8):
    # Load daily data
    data = load_json(f"data/daily/day_{day}.json")
    
    # Profile
    profile = profiler.profile_dataset(data, "transactions")
    
    # Track & alert
    metrics = monitor.track_profiling_metrics(profile, "transactions")
    alerts = monitor.check_thresholds(metrics)
    
    if alerts:
        print(f"Day {day}: {len(alerts)} alerts")
        for alert in alerts:
            print(f"  {alert.severity}: {alert.message}")

# Trend analysis
trend = monitor.detect_trends("transactions_amount_null_pct")
print(f"Null % trend: {trend['direction']}")
print(f"Rate of change: {trend['rate_of_change']:.2f}")

# Export metrics for dashboarding
monitor.export_metrics("monitoring_history.json")
```

### Example 5: Generate Test Reports

```python
from utils import ReportGenerator
from config import Config

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

# Generate Markdown report
ReportGenerator.generate_markdown_report(
    results,
    f"{Config.REPORTS_DIR}/test_report.md"
)
```

---

## 🎬 Demo Scenarios

### Financial Transaction Validation

**Scenario:** Validate financial transactions with regulatory constraints

**Features Demonstrated:**
- Transaction amount boundary testing
- Currency validation
- Compliance flag checking
- Fraud risk score validation
- Pattern matching for IDs

**Run the demo:**
```bash
python examples/demo_pipelines/financial_validation_demo.py
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Framework | LangChain |
| LLM | OpenAI GPT-4 |
| Data Processing | Pandas |
| Validation | Great Expectations (optional) |
| Testing | pytest |
| Schema | JSON Schema |

---

## 📊 Supported Test Types

| Test Type | Description | Example |
|-----------|-------------|---------|
| **Schema Compliance** | Validates data against schema | Type checking, required fields |
| **Boundary Testing** | Tests edge values | Min/max values, empty strings |
| **Null/Missing Tests** | Validates null handling | Required field nulls |
| **Type Validation** | Ensures correct data types | String vs integer |
| **Pattern Matching** | Regex pattern validation | Email, phone, ID formats |
| **Business Rules** | Domain-specific logic | Amount limits, status transitions |
| **Regression Tests** | Detects pipeline changes | Compare baseline vs current |
| **Edge Cases** | Unusual but valid scenarios | Zero values, special characters |

---

## 🔧 Configuration

Edit `src/config/settings.py` to customize:

```python
class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = "your-api-key"
    OPENAI_MODEL = "gpt-4"
    OPENAI_TEMPERATURE = 0.7
    
    # Test Generation
    DEFAULT_TEST_COUNT = 10
    MAX_SYNTHETIC_RECORDS = 100
    EDGE_CASE_COVERAGE = True
    
    # Validation
    STRICT_MODE = False
    ENABLE_AI_VALIDATION = True
    
    # Reporting
    DEFAULT_REPORT_FORMAT = "html"
```

---

## 📚 Documentation

- [Architecture Guide](docs/architecture.md) - System design and components
- [API Reference](docs/api_reference.md) - Detailed API documentation
- [Best Practices](docs/best_practices.md) - Testing best practices
- [Examples](examples/) - More usage examples

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_schema_analyzer.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [OpenAI GPT-4](https://openai.com/)
- Inspired by modern data quality frameworks

---

## 🗺️ Roadmap

- [ ] Integration with dbt for transformation testing
- [ ] Support for more schema formats (Avro, Protobuf)
- [ ] Real-time pipeline monitoring
- [ ] Multi-language support (TypeScript, Java)
- [ ] Cloud deployment templates (AWS, Azure, GCP)
- [ ] Visual test case builder
- [ ] Advanced ML-based anomaly detection

---

<div align="center">

**Made with ❤️ for the Data Engineering Community**

⭐ Star this repo if you find it helpful!

</div>
