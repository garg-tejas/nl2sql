"""
NL-to-SQL Pipeline - Flask Web Application

A modular pipeline for converting natural language to SQL using
open-source LLMs via HuggingFace Inference API.

Security features:
- Prompt injection detection and prevention
- Input validation and sanitization
- Output monitoring for data leakage
"""

from flask import Flask, render_template, request, jsonify
import traceback

from pipeline.schema_processor import format_schema_for_prompt
from pipeline.reasoning import plan_query
from pipeline.sql_generator import generate_sql, format_sql
from pipeline.verifier import verify_and_correct
from pipeline.answer_generator import generate_answer
from security import SecureLLMPipeline, SQL_SAFETY_DISCLAIMER
from config import ENABLE_SECURITY_LOGGING

app = Flask(__name__)

# Initialize security pipeline
security = SecureLLMPipeline(enable_logging=ENABLE_SECURITY_LOGGING)


@app.route('/')
def index():
    """Serve the main UI."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate SQL from natural language question.
    
    Expects JSON body with:
    - schema: Database schema (CREATE TABLE statements)
    - question: Natural language question
    
    Returns JSON with:
    - success: Boolean
    - sql: Generated SQL query
    - reasoning: Chain-of-thought explanation
    - verification: Verification status and any corrections
    - disclaimer: Security notice about SQL execution
    - error: Error message if failed
    """
    try:
        data = request.get_json()
        
        schema = data.get('schema', '').strip()
        question = data.get('question', '').strip()
        
        if not schema:
            return jsonify({
                'success': False,
                'error': 'Please provide a database schema'
            }), 400
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Please provide a question'
            }), 400
        
        # Security Layer: Validate and sanitize inputs
        validation = security.validate_input(question, schema)
        
        if not validation.is_safe:
            return jsonify({
                'success': False,
                'error': validation.rejection_reason,
                'security_blocked': True
            }), 400
        
        # Use sanitized input
        question = validation.sanitized_input
        
        # Step 1: Process and format the schema
        formatted_schema = format_schema_for_prompt(schema)
        
        # Step 2: Generate chain-of-thought reasoning
        reasoning = plan_query(question, formatted_schema)
        
        # Security: Validate LLM output for leakage
        reasoning = security.validate_output(reasoning)
        
        # Step 3: Generate SQL based on reasoning
        sql = generate_sql(question, formatted_schema, reasoning)
        
        # Step 4: Verify and correct SQL
        verification = verify_and_correct(sql, question, schema)
        
        # Format the final SQL
        final_sql = format_sql(verification.sql)
        
        # Security: Validate final SQL output
        final_sql = security.validate_output(final_sql)
        
        # Step 5: Generate human-readable answer
        answer = generate_answer(question, final_sql, reasoning)
        
        # Security: Validate answer output
        answer = security.validate_output(answer)
        
        return jsonify({
            'success': True,
            'sql': final_sql,
            'reasoning': reasoning,
            'answer': answer,
            'verification': {
                'is_valid': verification.is_valid,
                'corrections_made': verification.corrections_made,
                'notes': verification.errors
            },
            'disclaimer': SQL_SAFETY_DISCLAIMER
        })
        
    except ValueError as e:
        # Expected errors (API issues, etc.)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        # Unexpected errors
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("NL-to-SQL Pipeline (Secured)")
    print("=" * 60)
    print("\nSecurity features enabled:")
    print("  - Prompt injection detection")
    print("  - Input validation and sanitization")
    print("  - Output monitoring for data leakage")
    print(f"  - Security logging: {'enabled' if ENABLE_SECURITY_LOGGING else 'disabled'}")
    print("\nStarting server at http://localhost:5000")
    print("\nMake sure you have:")
    print("1. Added your HuggingFace API token to .env file")
    print("2. Installed requirements: pip install -r requirements.txt")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, port=5000)
