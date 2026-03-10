"""
SQL Agent — The brain that connects everything to Google Gemini

PURPOSE:
    This is the core module. It:
    1. Loads your database schemas (using schema_loader)
    2. Takes a user's natural language question
    3. Builds a prompt (using prompt_builder)
    4. Sends it to Google Gemini
    5. Returns the generated SQL query

HOW IT WORKS:
    The SQLAgent class is initialized once with the schema directory.
    On startup, it loads all schemas and configures the Gemini client.
    Then you call generate_query() with any question, and it returns SQL.
"""

import os
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from agent.schema_loader import load_schemas
from agent.prompt_builder import build_system_instruction, build_user_message


class SQLAgent:
    """
    AI-powered SQL query generator using Google Gemini.

    Usage:
        agent = SQLAgent(schema_dir="schemas")
        sql = agent.generate_query("Show all employees in Engineering")
        print(sql)
    """

    def __init__(self, schema_dir: str = "schemas", model: str = "gemini-flash-latest"):
        """
        Initialize the SQL Agent.

        This does three things:
        1. Loads the API key from your .env file
        2. Loads all schema files from the schema directory
        3. Sets up the Gemini client

        Args:
            schema_dir: Path to the folder containing .sql schema files.
            model: Which Gemini model to use. Default is "gemini-flash-latest"
                   (reliable free tier quota). Other options:
                   - "gemini-2.0-flash" (if enabled)
                   - "gemini-2.0-flash-lite"
        """
        # Step 1: Load environment variables (reads .env file)
        load_dotenv()

        # Step 2: Get the API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError(
                "[ERROR] GOOGLE_API_KEY not found or not set!\n"
                "   1. Copy .env.example to .env\n"
                "   2. Replace 'your-api-key-here' with your real API key\n"
                "   3. Get a free key at: https://aistudio.google.com/apikey"
            )

        # Step 3: Load the database schemas
        self.schema_text = load_schemas(schema_dir)

        # Step 4: Build the system instruction (tells Gemini who it is)
        self.system_instruction = build_system_instruction(self.schema_text)

        # Step 5: Create the Gemini client
        self.client = genai.Client(api_key=api_key)
        self.model = model

        print(f"[READY] SQL Agent ready! Using model: {model}")

    def set_schema(self, schema_text: str):
        """
        Dynamically update the agent's schema and rebuild the prompt.
        Also cleans up CSV-wrapped SQL (strips quotes/noise).
        """
        # Quick cleanup: If it's a CSV with SQL, it might have leading/trailing quotes
        cleaned = schema_text.strip()
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
            # Remove wrapping quotes if they encapsulate the whole content (common in CSV of 1 column)
            if cleaned.upper().count("CREATE TABLE") >= 1:
                cleaned = cleaned[1:-1]
        
        self.schema_text = cleaned
        self.system_instruction = build_system_instruction(self.schema_text)
        print("[UPDATED] SQL Agent schema changed (Smart Clean applied)!")

    def infer_schema_from_csv(self, csv_text: str, filename: str) -> str:
        """
        Use Gemini to infer a SQL schema from CSV data.
        
        Args:
            csv_text: Raw CSV string content.
            filename: Name of the file (used for table naming).
            
        Returns:
            A string containing the inferred CREATE TABLE statement.
        """
        table_name = os.path.splitext(filename)[0].lower().replace(" ", "_")
        
        # Take a sample of the CSV (first 10 rows) to keep the prompt concise
        lines = csv_text.splitlines()
        sample_data = "\n".join(lines[:10])
        
        prompt = f"""
        Analyze the following CSV data sample from a file named '{filename}'.
        Generate a single SQL 'CREATE TABLE {table_name}' statement that matches this data.
        Infer the most appropriate data types (e.g., INT, VARCHAR, DATE, DECIMAL) for each column based on the sample values.
        
        CSV SAMPLE:
        {sample_data}
        
        Return ONLY the SQL code. No markdown, no explanations.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            inferred_sql = response.text.strip()
            # Remove markdown code blocks if Gemini includes them
            if inferred_sql.startswith("```"):
                inferred_sql = "\n".join(inferred_sql.splitlines()[1:-1])
            
            return inferred_sql
        except Exception as e:
            print(f"Error inferring schema: {e}")
            raise Exception(f"Failed to infer schema from CSV: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate_query(self, user_question: str) -> str:
        """
        Generate a SQL query from a natural language question.
        Now includes retries for 503 (Busy) API errors.
        """
        # Build the user message
        user_message = build_user_message(user_question)

        # Call Gemini API
        response = self.client.models.generate_content(
            model=self.model,
            config={
                "system_instruction": self.system_instruction,
                "temperature": 0.1,
            },
            contents=user_message,
        )

        # Extract and clean the response text
        sql_query = response.text.strip()

        # Remove markdown code fences if Gemini wraps the SQL in them
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]  # Remove ```sql
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]  # Remove ```
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]  # Remove trailing ```

        return sql_query.strip()

    def get_schema(self) -> str:
        """Return the loaded schema text (useful for debugging)."""
        return self.schema_text
