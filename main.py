"""
Main Entry Point — Run your SQL Agent from the terminal

PURPOSE:
    This is the file you run to start the agent:
        python main.py

    It creates an interactive loop where you can:
    - Type a question → get a SQL query
    - Type 'schema' → see the loaded database schema
    - Type 'exit' or 'quit' → stop the program
"""

from agent.sql_agent import SQLAgent



def print_banner():
    """Print a welcome banner when the app starts."""
    print()
    print("=" * 60)
    print("  SQL Query Agent (Powered by Google Gemini)")
    print("=" * 60)
    print()
    print("  Ask me anything about your database in plain English,")
    print("  and I'll generate the SQL query for you!")
    print()
    print("  Commands:")
    print("    schema  — Show the loaded database schema")
    print("    exit    — Quit the program")
    print()
    print("-" * 60)


def main():
    """Main function — sets up the agent and starts the chat loop."""

    print_banner()

    # Initialize the agent (loads schemas + connects to Gemini)
    try:
        agent = SQLAgent(schema_dir="schemas")
    except (FileNotFoundError, ValueError) as e:
        print(f"\n{e}")
        return

    print()

    # Interactive loop — keeps running until user types 'exit'
    while True:
        try:
            # Get user input
            user_input = input(">> Your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C gracefully
            print("\n\nGoodbye!")
            break

        # Skip empty input
        if not user_input:
            continue

        # Check for exit commands
        if user_input.lower() in ("exit", "quit", "q"):
            print("\nGoodbye!")
            break

        # Check for special commands
        if user_input.lower() == "schema":
            print("\n[SCHEMA] Loaded Schema:")
            print("-" * 40)
            print(agent.get_schema())
            print("-" * 40)
            print()
            continue

        # Generate the SQL query
        print("\n[...] Generating SQL query...\n")
        try:
            sql = agent.generate_query(user_input)
            print("[OK] Generated SQL Query:")
            print("-" * 40)
            print(sql)
            print("-" * 40)
        except Exception as e:
            print(f"[ERROR] Error generating query: {e}")

        print()  # Add spacing between questions


if __name__ == "__main__":
    main()
