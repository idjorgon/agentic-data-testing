"""
Demo Pipeline: Financial Transaction Validation
Demonstrates how to use the agentic testing framework for financial data validation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents import OrchestratorAgent
from utils import load_json, ReportGenerator, setup_logger
from config import Config

# Setup logging
logger = setup_logger("financial_pipeline", level="INFO")


def run_financial_validation_pipeline():
    """
    Run complete financial transaction validation pipeline
    """
    logger.info("=" * 80)
    logger.info("Starting Financial Transaction Validation Pipeline")
    logger.info("=" * 80)
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Load schema and data
    schema_path = Config.SCHEMA_DIR / "financial_transaction_schema.json"
    data_path = Config.DATA_DIR / "financial_transactions.json"
    
    logger.info(f"Loading schema from: {schema_path}")
    schema = load_json(schema_path)
    
    logger.info(f"Loading data from: {data_path}")
    test_data = load_json(data_path)
    logger.info(f"Loaded {len(test_data)} transactions")
    
    # Define business rules for financial transactions
    business_rules = [
        {
            "name": "amount_positive",
            "type": "range",
            "field": "amount",
            "min": 0.01,
            "max": 1000000.00,
            "description": "Transaction amount must be positive and within limits"
        },
        {
            "name": "valid_currency",
            "type": "custom",
            "expression": "currency must be a valid ISO 4217 code",
            "description": "Currency must be valid"
        },
        {
            "name": "transaction_id_format",
            "type": "pattern",
            "field": "transaction_id",
            "pattern": "^TXN[0-9]{10}$",
            "description": "Transaction ID must follow TXN + 10 digits format"
        },
        {
            "name": "high_risk_monitoring",
            "type": "range",
            "field": "risk_score",
            "min": 0,
            "max": 100,
            "description": "Risk score must be between 0-100"
        }
    ]
    
    # Execute test workflow
    logger.info("\n" + "=" * 80)
    logger.info("Executing Test Workflow")
    logger.info("=" * 80)
    
    results = orchestrator.execute_test_workflow(
        schema=schema,
        test_data=test_data,
        business_rules=business_rules
    )
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("Workflow Results")
    logger.info("=" * 80)
    
    for step in results["steps"]:
        logger.info(f"\n📋 {step['step'].upper()}")
        logger.info(f"   Status: {step['status']}")
        if "result" in step:
            for key, value in step["result"].items():
                if key != "insights":
                    logger.info(f"   {key}: {value}")
    
    # Generate insights interpretation
    logger.info("\n" + "=" * 80)
    logger.info("Interpreting Results")
    logger.info("=" * 80)
    
    interpretation = orchestrator.interpret_results(results)
    logger.info(f"\n{interpretation}")
    
    # Generate reports
    logger.info("\n" + "=" * 80)
    logger.info("Generating Reports")
    logger.info("=" * 80)
    
    # Create sample execution results for report
    execution_results = {
        "total_tests": len(test_data) * 3,  # Multiple test types per record
        "passed": int(len(test_data) * 2.7),  # ~90% pass rate
        "failed": int(len(test_data) * 0.3),
        "pass_rate": 90.0,
        "test_results": [
            {
                "test_name": f"Schema validation for transaction {i+1}",
                "test_type": "schema_compliance",
                "passed": True
            }
            for i in range(len(test_data))
        ]
    }
    
    # Generate HTML report
    html_report_path = Config.REPORTS_DIR / "financial_validation_report.html"
    ReportGenerator.generate_html_report(execution_results, str(html_report_path))
    logger.info(f"✅ HTML report saved to: {html_report_path}")
    
    # Generate Markdown report
    md_report_path = Config.REPORTS_DIR / "financial_validation_report.md"
    ReportGenerator.generate_markdown_report(execution_results, str(md_report_path))
    logger.info(f"✅ Markdown report saved to: {md_report_path}")
    
    # Generate JSON report
    json_report_path = Config.REPORTS_DIR / "financial_validation_report.json"
    ReportGenerator.generate_json_report(execution_results, str(json_report_path))
    logger.info(f"✅ JSON report saved to: {json_report_path}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Pipeline Completed Successfully!")
    logger.info("=" * 80)
    
    return results


if __name__ == "__main__":
    try:
        results = run_financial_validation_pipeline()
        print("\n✨ Financial validation pipeline completed successfully!")
        print(f"📊 Check the reports directory for detailed results: {Config.REPORTS_DIR}")
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        sys.exit(1)
