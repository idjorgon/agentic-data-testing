"""
Report generation utilities
"""

from typing import Dict, List, Any
from datetime import datetime
import json
from pathlib import Path


class ReportGenerator:
    """Generate test execution reports in various formats"""
    
    @staticmethod
    def generate_html_report(results: Dict[str, Any], output_path: str):
        """
        Generate HTML test report
        
        Args:
            results: Test execution results
            output_path: Path to save HTML report
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
        }}
        .summary {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 5px;
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            font-size: 14px;
            color: #7f8c8d;
        }}
        .passed {{
            color: #27ae60;
        }}
        .failed {{
            color: #e74c3c;
        }}
        .test-result {{
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
            border-radius: 3px;
        }}
        .test-result.passed {{
            border-left-color: #27ae60;
        }}
        .test-result.failed {{
            border-left-color: #e74c3c;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Test Execution Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="metric">
            <div class="metric-value">{results.get('total_tests', 0)}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value passed">{results.get('passed', 0)}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric">
            <div class="metric-value failed">{results.get('failed', 0)}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{results.get('pass_rate', 0):.1f}%</div>
            <div class="metric-label">Pass Rate</div>
        </div>
    </div>
    
    <div class="summary">
        <h2>Test Results</h2>
        """
        
        for test_result in results.get('test_results', []):
            status = "passed" if test_result.get('passed') else "failed"
            status_icon = "✅" if test_result.get('passed') else "❌"
            
            html_content += f"""
        <div class="test-result {status}">
            <h3>{status_icon} {test_result.get('test_name', 'Unnamed Test')}</h3>
            <p><strong>Type:</strong> {test_result.get('test_type', 'N/A')}</p>
            <p><strong>Status:</strong> {status.upper()}</p>
        </div>
            """
        
        html_content += """
    </div>
</body>
</html>
        """
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    @staticmethod
    def generate_markdown_report(results: Dict[str, Any], output_path: str):
        """
        Generate Markdown test report
        
        Args:
            results: Test execution results
            output_path: Path to save Markdown report
        """
        md_content = f"""# Test Execution Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {results.get('total_tests', 0)} |
| Passed | {results.get('passed', 0)} ✅ |
| Failed | {results.get('failed', 0)} ❌ |
| Pass Rate | {results.get('pass_rate', 0):.1f}% |

## Test Results

"""
        
        for test_result in results.get('test_results', []):
            status_icon = "✅" if test_result.get('passed') else "❌"
            
            md_content += f"""
### {status_icon} {test_result.get('test_name', 'Unnamed Test')}

- **Type:** {test_result.get('test_type', 'N/A')}
- **Status:** {'PASSED' if test_result.get('passed') else 'FAILED'}

"""
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(md_content)
    
    @staticmethod
    def generate_json_report(results: Dict[str, Any], output_path: str):
        """
        Generate JSON test report
        
        Args:
            results: Test execution results
            output_path: Path to save JSON report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "results": results
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
