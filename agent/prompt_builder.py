"""
Prompt Builder — Crafts the instructions we send to Gemini

PURPOSE:
    This module builds the two key pieces of text that tell the AI
    how to behave and what to do:

    1. SYSTEM INSTRUCTION — Tells Gemini "you are a SQL expert" and
       gives it the database schema to reference.

    2. USER MESSAGE — The actual question the user is asking,
       e.g., "Show all employees hired in 2024."

    By separating prompt construction into its own module, we can
    easily tweak the instructions without touching the rest of the code.
"""


def build_system_instruction(schema_text: str) -> str:
    """
    Build the system instruction that tells Gemini who it is
    and gives it the database schema.

    The system instruction is like a "personality" for the AI.
    It runs BEFORE the user's question and sets the context.

    Args:
        schema_text: The combined SQL schema definitions.

    Returns:
        A system instruction string for Gemini.
    """
    return f"""You are an expert SQL query generator. Your job is to write accurate, 
efficient SQL queries based on the database schema provided below.

RULES:
1. Only use tables and columns that exist in the schema below.
2. Return ONLY the SQL query — no explanations, no markdown formatting.
3. If the user's request is ambiguous, make reasonable assumptions and 
   add a brief SQL comment (--) explaining your assumption.
4. Use proper JOIN syntax (never comma-separated joins).
5. Use aliases for readability when joining multiple tables.
6. If the request cannot be answered with the given schema, respond with 
   a SQL comment explaining why.

DATABASE SCHEMA:
{schema_text}
"""


def build_user_message(user_question: str) -> str:
    """
    Build the user message — this is the actual question being asked.

    We wrap it lightly to make the intent clear to the AI.

    Args:
        user_question: The natural language question from the user.

    Returns:
        A formatted user message string.
    """
    return f"Write a SQL query for the following request: {user_question}"
