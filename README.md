# 🗄️ SQL Query Agent

An AI-powered agent that generates SQL queries from plain English questions using **Google Gemini**.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your API key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and paste your API key
# Get a free key at: https://aistudio.google.com/apikey
```

### 3. Run the agent

```bash
python main.py
```

### 4. Ask questions!

```
📝 Your question: Show all employees in the Engineering department
✅ Generated SQL Query:
----------------------------------------
SELECT e.*
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'Engineering';
----------------------------------------
```

## Adding Your Own Schemas

1. Place your `.sql` schema files in the `schemas/` folder
2. The agent automatically loads all `.sql` files on startup
3. Restart the agent to pick up new schemas

## Commands

| Command | What it does |
|---------|-------------|
| `schema` | Show the loaded database schema |
| `exit` | Quit the program |

## Project Structure

```
├── schemas/              # Your .sql schema files go here
│   └── sample.sql        # Example HR schema (5 tables)
├── agent/
│   ├── schema_loader.py  # Reads schema files
│   ├── prompt_builder.py # Builds prompts for Gemini
│   └── sql_agent.py      # Core agent (Gemini API calls)
├── main.py               # Run this to start the agent
├── requirements.txt      # Python dependencies
└── .env.example          # API key template
```
