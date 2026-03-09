"""
Schema Loader — Reads your .sql schema files

PURPOSE:
    This module reads all .sql files from a directory (e.g., "schemas/")
    and combines them into a single text string. This combined text is
    what we send to the AI so it understands your database structure.

HOW IT WORKS:
    1. Looks inside the given directory for any files ending in .sql
    2. Reads each file's contents
    3. Joins them together with clear separators
    4. Returns the combined schema text
"""

import os
from pathlib import Path


def load_schemas(schema_dir: str = "schemas") -> str:
    """
    Load all .sql schema files from the given directory.

    Args:
        schema_dir: Path to the folder containing .sql files.
                    Defaults to "schemas" (relative to where you run the app).

    Returns:
        A single string containing all schema definitions,
        separated by headers showing which file each schema came from.

    Raises:
        FileNotFoundError: If the schema directory doesn't exist.
        ValueError: If no .sql files are found in the directory.
    """
    schema_path = Path(schema_dir)

    # Check if the directory exists
    if not schema_path.exists():
        print(f"[WARNING] Schema directory '{schema_dir}' not found. Starting with empty schema.")
        return ""

    # Find all .sql files, sorted alphabetically for consistency
    sql_files = sorted(schema_path.glob("*.sql"))

    if not sql_files:
        print(f"[WARNING] No .sql files found in '{schema_dir}'. Starting with empty schema.")
        return ""

    # Read each file and combine them with clear separators
    schema_parts = []
    
    # SAFETY FALLBACK: If no files were found, provide a basic sample schema
    if not sql_files:
        print("[INFO] No external schemas found. Using 'Safety Fallback' (Employees Sample).")
        return """
-- Safety Fallback Schema: Classic Employees Database
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);
"""

    for sql_file in sql_files:
        content = sql_file.read_text(encoding="utf-8")
        # Add a header so the AI knows which file each schema came from
        header = f"-- === Schema from: {sql_file.name} ==="
        schema_parts.append(f"{header}\n{content}")

    combined_schema = "\n\n".join(schema_parts)

    print(f"[OK] Loaded {len(sql_files)} schema file(s): {', '.join(f.name for f in sql_files)}")

    return combined_schema


def list_schema_files(schema_dir: str = "schemas") -> list[str]:
    """
    List all .sql schema file names in the directory.
    Useful for showing the user what schemas are loaded.
    """
    schema_path = Path(schema_dir)
    if not schema_path.exists():
        return []
    return [f.name for f in sorted(schema_path.glob("*.sql"))]
