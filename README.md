# NL-2-SQL: Natural Language to SQL Pipeline

A modular, interpretable pipeline that converts natural language questions into SQL queries using open-source LLMs via HuggingFace.

## Features

| Requirement | Implementation |
|-------------|----------------|
| Takes natural language questions as input | Web UI with question input and example queries |
| Reasons about the database schema | Chain-of-thought prompting breaks down query logic step-by-step |
| Generates safe, efficient SQL | LLM generates SQL with syntax verification and auto-correction |
| Returns human-readable answers | "In Plain English" section explains what the query does |
| Shows its reasoning | Displays numbered reasoning steps for transparency |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Flask Web UI                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Pipeline Modules                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Schema     │→ │  Reasoning   │→ │     SQL      │           │
│  │  Processor   │  │   (CoT)      │  │  Generator   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                              │                  │
│                                              ▼                  │
│                    ┌──────────────┐  ┌──────────────┐           │
│                    │   Answer     │← │   Verifier   │           │
│                    │  Generator   │  │ & Corrector  │           │
│                    └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    HuggingFace Inference API
                    (Qwen/Qwen3-Coder-30B-A3B-Instruct)
```

## Pipeline Steps

1. **Schema Processing** - Parses CREATE TABLE statements to understand database structure
2. **Chain-of-Thought Reasoning** - Breaks down the question into logical steps (tables needed, joins, filters, etc.)
3. **SQL Generation** - Generates SQL based on the reasoning
4. **Verification & Correction** - Validates syntax and schema references, auto-corrects errors
5. **Answer Generation** - Produces a human-readable explanation of what the query does

## Why No SQL Execution?

We intentionally designed this as a **query generation** tool rather than an execution engine for several important reasons:

1. **Security** - Executing arbitrary SQL on real databases poses significant security risks (SQL injection, data exposure, accidental data modification)

2. **Flexibility** - Users can review and modify the generated SQL before running it on their own databases with proper access controls

3. **Database Agnostic** - The tool works with any SQL dialect without needing database connections or credentials

4. **Educational Focus** - The transparent reasoning and human-readable explanations help users understand SQL, not just execute it

5. **Production Safety** - In real-world scenarios, generated SQL should always be reviewed by a human before execution

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure HuggingFace API token:**
   - Get a free token at: https://huggingface.co/settings/tokens
   - Create a `.env` file:
     ```
     HF_API_TOKEN=hf_your_token_here
     ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

## Usage

1. **Define Schema** - Paste your CREATE TABLE statements
2. **Ask Question** - Type your question in natural language
3. **Generate** - Click to generate SQL with full reasoning
4. **Review** - See the human-readable answer, SQL query, and step-by-step reasoning

## Tech Stack

- **Backend:** Python, Flask
- **LLM:** Qwen/Qwen3-Coder-30B-A3B-Instruct (via HuggingFace Inference API)
- **SQL Parsing:** sqlparse
- **Frontend:** Vanilla HTML/CSS/JavaScript

## Project Structure

```
├── app.py                 # Flask application
├── config.py              # Configuration and prompts
├── pipeline/
│   ├── schema_processor.py   # Schema parsing
│   ├── reasoning.py          # Chain-of-thought reasoning
│   ├── sql_generator.py      # SQL generation
│   ├── verifier.py           # Syntax verification
│   └── answer_generator.py   # Human-readable answers
├── utils/
│   └── hf_client.py          # HuggingFace API client
├── templates/
│   └── index.html            # Web UI
└── static/
    └── styles.css            # Styling
```

## License

MIT License


