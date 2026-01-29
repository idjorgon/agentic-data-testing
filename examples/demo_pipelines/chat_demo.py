"""
Demo: Interactive Chat with Orchestrator Agent
Demonstrates the conversational interface for test planning and results interpretation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents import OrchestratorAgent
from utils import load_json, setup_logger
from config import Config

# Setup logging
logger = setup_logger("chat_demo", level="INFO")


def interactive_demo():
    """
    Run interactive demo with the orchestrator agent
    """
    print("=" * 80)
    print("🤖 AI Agentic Test Planning Assistant")
    print("=" * 80)
    print("\nWelcome! I'm your intelligent test planning assistant.")
    print("I can help you:")
    print("  • Plan comprehensive test strategies")
    print("  • Generate test cases based on schemas")
    print("  • Validate data and pipelines")
    print("  • Interpret test results")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Load sample schema for context
    schema_path = Config.SCHEMA_DIR / "financial_transaction_schema.json"
    schema = load_json(schema_path)
    
    context = {
        "schema": schema,
        "domain": "financial_transactions"
    }
    
    # Sample conversation starters
    sample_questions = [
        "What tests should I create for this financial transaction schema?",
        "How can I validate large transactions for compliance?",
        "What edge cases should I test for transaction amounts?",
        "Create a test strategy for fraud detection"
    ]
    
    print("💡 Try asking questions like:")
    for i, q in enumerate(sample_questions, 1):
        print(f"   {i}. {q}")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! Happy testing!")
                break
            
            # Get response from orchestrator
            response = orchestrator.chat(user_input, context=context)
            
            print(f"\n🤖 Assistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"\n❌ Error: {str(e)}\n")


def scripted_demo():
    """
    Run a scripted demo showing typical interactions
    """
    print("=" * 80)
    print("🎬 Scripted Demo: AI Test Planning Conversation")
    print("=" * 80)
    
    orchestrator = OrchestratorAgent()
    
    # Load schema
    schema_path = Config.SCHEMA_DIR / "financial_transaction_schema.json"
    schema = load_json(schema_path)
    
    context = {"schema": schema}
    
    # Simulated conversation
    conversations = [
        "What are the most important tests for this financial transaction schema?",
        "How should I test for compliance with transaction amount limits?",
        "What synthetic test data should I generate for edge cases?",
        "Create a test plan for validating high-risk transactions"
    ]
    
    print("\n🎭 Simulating conversation with AI agent...\n")
    
    for question in conversations:
        print(f"👤 User: {question}\n")
        response = orchestrator.chat(question, context=context)
        print(f"🤖 Assistant: {response}\n")
        print("-" * 80 + "\n")
    
    print("✨ Demo completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Test Planning Chat Demo")
    parser.add_argument(
        "--mode",
        choices=["interactive", "scripted"],
        default="scripted",
        help="Demo mode: interactive or scripted"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "interactive":
            interactive_demo()
        else:
            scripted_demo()
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
        sys.exit(1)
