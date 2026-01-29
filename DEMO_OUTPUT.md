# Chat Demo Output & Guide

## What This Demo Does

The **chat_demo.py** demonstrates the AI-powered conversational interface of the Agentic Data Testing Framework. It shows how the Orchestrator Agent uses GPT-4 to provide intelligent, context-aware responses about test planning, strategy, and data validation.

### Key Capabilities Demonstrated:

1. **Intelligent Test Planning** - AI analyzes schemas and recommends comprehensive test strategies
2. **Context-Aware Responses** - Agent understands the financial transaction schema and provides domain-specific guidance
3. **Test Strategy Generation** - Creates detailed test plans for specific scenarios (e.g., high-risk transactions)
4. **Edge Case Identification** - Suggests synthetic data for boundary and edge case testing
5. **Conversational Interface** - Natural language Q&A about testing approaches

---

## How to Run This Demo

### Quick Start

```bash
# Make sure you're in the project directory and venv is activated
cd agentic-data-testing
source venv/bin/activate

# Run scripted demo (automated conversation)
python examples/demo_pipelines/chat_demo.py --mode scripted

# Run interactive mode (you ask questions)
python examples/demo_pipelines/chat_demo.py --mode interactive
```

### Prerequisites

- Virtual environment activated
- Dependencies installed (`pip install -r requirements.txt`)
- OpenAI API key configured in `.env` file

---

## Demo Output

```
================================================================================
🎬 Scripted Demo: AI Test Planning Conversation
================================================================================

🎭 Simulating conversation with AI agent...

👤 User: What are the most important tests for this financial transaction schema?

🤖 Assistant: Based on the provided schema, here are the most important tests you should consider:

1. **Required Field Tests**: Verify that all the required fields are present. For this schema, the required fields are transaction_id, account_id, transaction_date, amount, currency, transaction_type, and status.

2. **Data Type Tests**: Verify that all fields contain data of the correct type. For example, transaction_id should be a string, amount should be a number, and compliance_flags should be an array.

3. **Format Tests**: Validate data format for fields that have specific format or pattern requirements. For instance, transaction_id should match the pattern "^TXN[0-9]{10}$", transaction_date should be in date-time format, and ip_address should be in ipv4 format.

4. **Range Tests**: Check that numeric fields fall within the specified range. The amount should be between 0.01 and 1,000,000. The fee should be between 0 and 1000, and risk_score should be between 0 and 100.

5. **Enumeration Tests**: Validate that fields with enumerated allowable values only contain one of those values. The currency field should only contain one of "USD", "EUR", "GBP", "JPY", "CAD", and transaction_type and status fields have their own specific allowable values too.

6. **Length Tests**: Confirm that string fields adhere to the length constraints. For instance, transaction_id length should be 13 characters.

7. **Uniqueness Tests**: For the compliance_flags array, ensure that it only contains unique items.

8. **Business Rule Tests**: These are specific to how your application uses the data. Examples might include checking that a transaction with status "COMPLETED" has a balance_after value, or that transactions with a high risk_score also have relevant entries in the compliance_flags array.

To execute these tests, you could use a combination of automated testing frameworks and manual validation. For example, you could use a JSON Schema validation library to easily check most of these rules, and write custom code or use a data testing tool for any that require more complex validation.

--------------------------------------------------------------------------------

👤 User: How should I test for compliance with transaction amount limits?

🤖 Assistant: In order to test for compliance with transaction amount limits as defined in your financial transaction schema, you can follow the steps below:

1. **Boundary Value Analysis (BVA)**: Test the boundaries of the "amount" field. This includes the lower limit (0.01), the upper limit (1,000,000), and values just beyond these limits. Here are some test cases:
   - Test Case 1: Provide an amount of 0.01 (Lower limit)
   - Test Case 2: Provide an amount of 1,000,000 (Upper limit)
   - Test Case 3: Provide an amount slightly lower than the lower limit, e.g., 0.009
   - Test Case 4: Provide an amount slightly higher than the upper limit, e.g., 1,000,000.01

2. **Equivalence Partitioning (EP)**: Divide the "amount" field into equivalent classes where you can expect the same behavior. For example, valid and invalid classes. Here are some test cases:
   - Test Case 5: Provide an amount from the valid class, e.g., 500,000 (Any value within the range of 0.01 and 1,000,000)
   - Test Case 6: Provide an amount from the invalid class, e.g., -1 or 1,000,001 (Any value outside the range of 0.01 and 1,000,000)

3. **Error Guessing**: This is based on the tester's experience and intuition. You can test with some random values which might cause the system to fail, such as a string instead of a number, or a very large number.

4. **Regression Testing**: After any bugs found from the above tests are fixed, perform regression testing to ensure that the fixes haven't broken anything else and that the "amount" field still behaves correctly with other test cases.

Remember to verify whether the system correctly accepts or rejects the transaction based on the amount, and whether any appropriate error messages are displayed in the case of invalid amounts.

Automated testing tools can be very useful for executing these tests, especially if you are dealing with large amounts of data. However, manual testing may also be suitable, especially for error guessing and exploratory testing.

--------------------------------------------------------------------------------

👤 User: What synthetic test data should I generate for edge cases?

🤖 Assistant: Based on your financial transaction schema, here are some synthetic test data suggestions for edge cases:

1. **transaction_id**: Generate transaction IDs that don't follow the pattern "^TXN[0-9]{10}$". For example, "TXN123", "1234567890", "TXN12345678901".

2. **account_id**: Generate account IDs that don't follow the pattern "^ACC[0-9]{8}$". For example, "ACC123", "12345678", "ACC123456789".

3. **transaction_date**: Use dates that are not in the correct format. For example, "01-01-2021", "2021.01.01", "01/01/21".

4. **amount**: Use values that are outside the range of 0.01 to 1,000,000. For example, -1, 0, 1,000,000.01.

5. **currency**: Use currency codes that are not in the enumerated list. For example, "ABC", "XYZ", "123".

6. **transaction_type**: Use transaction types that are not in the enumerated list. For example, "LOAN", "REWARD", "INTEREST".

7. **status**: Use statuses that are not in the enumerated list. For example, "IN PROCESS", "DECLINED", "REVERSED".

8. **merchant_name**: Use names longer than 100 characters.

9. **merchant_category**: Generate merchant categories that don't follow the pattern "^[0-9]{4}$". For example, "123", "12345", "ABCD".

10. **description**: Use descriptions longer than 500 characters.

11. **fee**: Use values that are outside the range of 0 to 1000. For example, -1, 1,001.

12. **ip_address**: Use addresses that are not in the correct IPv4 format. For example, "256.0.0.1", "192.168.1", "1234.567.890.12".

13. **risk_score**: Use values that are outside the range of 0 to 100. For example, -1, 101.

14. **compliance_flags**: Use arrays that contain duplicate items. For example, ["flag1", "flag2", "flag1"].

Generate these edge case data and validate if the system correctly handles these invalid inputs, whether by rejecting the transaction, providing an appropriate error message, or correcting the data if applicable. This will help ensure that your system is robust and can handle unexpected data gracefully.

--------------------------------------------------------------------------------

👤 User: Create a test plan for validating high-risk transactions

🤖 Assistant: Sure, here is a comprehensive test plan to validate high-risk transactions based on your financial transaction schema:

**Test Plan: High-Risk Transaction Validation**

**Objective:** Validate the handling and processing of high-risk transactions.

**Scope:** All financial transactions classified as high-risk (risk_score > 70 for example, or any threshold set by your risk management team).

**Test Strategy:**

1. **Data Integrity Testing**: Verify that the high-risk transactions adhere to the specified schema. Use synthetic data to generate test cases.

2. **Risk Score Validation**: Verify that the risk score calculation is accurate and correctly classifies transactions as high-risk. Test with both synthetic and real data, if available.

3. **Compliance Flag Testing**: Verify that high-risk transactions correctly trigger compliance flags.

4. **Transaction Status Testing**: Verify that high-risk transactions are correctly marked with the appropriate status (e.g., "PENDING" for manual review).

5. **Notification Testing**: Verify that the system correctly sends notifications or alters relevant parties when a high-risk transaction is detected.

6. **Audit Trail Testing**: Verify that high-risk transactions are properly logged for audit purposes.

7. **Security Testing**: Ensure that high-risk transactions do not expose sensitive customer data.

8. **Performance Testing**: Check how the system performs under the load of a high volume of high-risk transactions.

**Test Cases:**

1. Create a transaction with a risk score over the high-risk threshold (e.g., 80) and verify it's correctly flagged as high-risk.
2. Create a transaction with a risk score just under the high-risk threshold (e.g., 69) and verify it's not flagged as high-risk.
3. Create a high-risk transaction and verify the status is correctly set (e.g., "PENDING").
4. Create a high-risk transaction and verify the compliance flags are triggered appropriately.
5. Create a high-risk transaction and verify the system sends a notification/alert.
6. Create a high-risk transaction and verify it's correctly logged in the audit trail.
7. Create a high volume of high-risk transactions and assess the system's performance.

**Test Environment:** A copy of the production environment where high-risk transactions can be simulated without risk.

**Test Data:** A mix of synthetic and real data (if available), including edge cases for high-risk transactions.

**Test Tools:** Automated testing tools for running test cases, performance testing tools for load testing, and log analysis tools for checking audit trails.

**Success Criteria:** All test cases pass and the system is able to correctly identify, process, and handle high-risk transactions according to the specified requirements.

**Test Schedule:** Depending on the complexity of the system and the number of test cases, this might take several days to a week.

**Responsibilities:** Assign a dedicated team or individual to carry out the test plan, including creating and executing test cases, and documenting and analyzing results.

**Approvals:** Obtain necessary approvals from stakeholders before proceeding with the test plan. This might include management, the risk management team, and the compliance team.

Remember to document all the test results and any issues found during testing, and to retest after any bugs have been fixed. This test plan should be part of your overall testing strategy and should be updated as necessary to reflect changes in the system or regulatory requirements.

--------------------------------------------------------------------------------

✨ Demo completed!
```

---

## What Makes This Powerful

### 🎯 Schema-Aware Intelligence

The AI agent automatically understands the financial transaction schema structure and provides relevant recommendations:
- Identifies all 7 required fields
- Recognizes data type constraints
- Understands pattern requirements (e.g., `TXN[0-9]{10}`)
- Knows the valid ranges for numeric fields

### 🧪 Professional Testing Methodologies

The agent applies industry-standard testing techniques:
- **Boundary Value Analysis (BVA)** - Testing min/max limits
- **Equivalence Partitioning** - Grouping similar test cases
- **Error Guessing** - Experience-based edge cases
- **Regression Testing** - Ensuring fixes don't break other features

### 📋 Comprehensive Test Planning

For high-risk transactions, the agent generates a complete test plan including:
- Clear objectives and scope
- Multiple testing strategies (integrity, compliance, security, performance)
- Specific test cases
- Success criteria
- Scheduling and responsibilities

### 💬 Natural Language Interface

Ask questions in plain English and get expert-level responses:
- "What tests should I create?"
- "How do I validate compliance?"
- "What edge cases should I consider?"

---

## Try Interactive Mode

Want to ask your own questions? Run:

```bash
python examples/demo_pipelines/chat_demo.py --mode interactive
```

Then ask questions like:
- "How should I test duplicate transactions?"
- "What validations are needed for international transfers?"
- "Create a test strategy for fraud detection"
- "What are the critical test areas for this schema?"

---

## Behind the Scenes

The demo uses:
- **Orchestrator Agent** - Coordinates the conversation
- **GPT-4** - Provides intelligent responses
- **Schema Context** - Financial transaction schema from `examples/sample_schemas/`
- **LangChain** - Manages the AI conversation flow

---

## Next Steps

1. **Run the full validation pipeline**: `python examples/demo_pipelines/financial_validation_demo.py`
2. **Generate test cases programmatically**: See the TestGeneratorAgent
3. **Validate your own data**: Load your schema and data files
4. **Extend the framework**: Add custom agents or validators

---

**Note**: This demo requires an OpenAI API key configured in your `.env` file. The AI responses may vary slightly between runs due to the model's creative nature, but the core recommendations remain consistent and valuable.
