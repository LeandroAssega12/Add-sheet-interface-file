import os
import sys
from pathlib import Path
import subprocess
from dotenv import load_dotenv
from typing import Tuple

# Load .env
ENV_PATH = Path(__file__).parent / "config" / ".env"
if ENV_PATH.exists():
    load_dotenv(str(ENV_PATH))

def generate_rating_component_list() -> Tuple[bool, str, str, int]:
    """
    Execute rating component list query using sqlplus.
    
    Returns:
        Tuple[bool, str, str, int]: (success, stdout, stderr, exit_code)
    """
    # Read DB connection parts (user/password@ALIAS_TNS)
    SQL_USERNAME = os.getenv("SQL_USERNAME")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_DATABASE = os.getenv("SQL_DATABASE")

    # Validate required vars
    if not SQL_USERNAME or not SQL_PASSWORD or not SQL_DATABASE:
        return False, "", "ERROR: Set SQL_USERNAME, SQL_PASSWORD and SQL_DATABASE in config/.env", 1

    # Paths
    LOCAL_SQL = Path(__file__).parent / "SQL_files" / "rating_component_list.sql"

    if not LOCAL_SQL.exists():
        return False, "", f"ERROR: Local SQL not found: {LOCAL_SQL}", 1

    try:
        # Build connection string and run sqlplus locally
        conn = f"{SQL_USERNAME}/{SQL_PASSWORD}@{SQL_DATABASE}"
        sql_dir = LOCAL_SQL.parent
        sql_file = LOCAL_SQL.name
        connection_string = f'cd "{sql_dir}" && sqlplus -s {conn} @{sql_file}'
        print(f"Executing command: {connection_string}", flush=True)
        
        # Execute sqlplus locally using subprocess
        result = subprocess.run(connection_string, shell=True, capture_output=True, text=True, timeout=900)
        out = result.stdout.rstrip()
        err = result.stderr.rstrip()
        exit_code = result.returncode

        print("SQL*Plus exit status:", exit_code)
        if out:
            print("--- STDOUT ---")
            print(out)
        if err:
            print("--- STDERR ---")
            print(err)

        # Clean up the output file - remove empty lines
        output_file = sql_dir / "rating_component_list.csv"
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Remove empty lines and write back
                cleaned_lines = [line for line in lines if line.strip()]
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.writelines(cleaned_lines)
                    
                print(f"Cleaned output file: {output_file}")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean output file: {cleanup_error}")

        return exit_code == 0, out, err, exit_code
        
    except Exception as e:
        error_msg = f"ERROR: {e}"
        print(error_msg)
        return False, "", error_msg, 1

if __name__ == "__main__":
    success, stdout, stderr, exit_code = generate_rating_component_list()
    sys.exit(exit_code)
