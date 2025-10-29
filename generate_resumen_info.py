import os
import sys
from pathlib import Path
import subprocess
from dotenv import load_dotenv
from typing import Tuple, Optional

# Load .env
ENV_PATH = Path(__file__).parent / "config" / ".env"
if ENV_PATH.exists():
    load_dotenv(str(ENV_PATH))

def generate_resumen_info(line_number: int) -> Tuple[bool, str, str, int]:
    """
    Execute generate resumen info by reading parameters from rates_info_search.csv.
    Reads the specified line from rates_info_search.csv and extracts 10 parameters.
    
    Args:
        line_number: Line number to read from rates_info_search.csv (1-based)
    
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
    LOCAL_SQL = Path(__file__).parent / "SQL_files" / "generate_resumen_infos.sql"
    RATES_FILE = Path(__file__).parent / "SQL_files" / "rates_info_search.csv"

    if not LOCAL_SQL.exists():
        return False, "", f"ERROR: Local SQL not found: {LOCAL_SQL}", 1
    
    if not RATES_FILE.exists():
        return False, "", f"ERROR: Rates file not found: {RATES_FILE}", 1

    try:
        # Read the specified line from rates_info_search.csv
        with open(RATES_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            if not lines:
                return False, "", "ERROR: Rates file is empty", 1
            
            if line_number < 1 or line_number > len(lines):
                return False, "", f"ERROR: Line number {line_number} is out of range. File has {len(lines)} lines", 1
            
            # Get the specified line (convert to 0-based index)
            target_line = lines[line_number - 1].strip()
            if not target_line:
                return False, "", f"ERROR: Line {line_number} is empty", 1
            
            # Split by comma and extract 10 parameters
            columns = target_line.split(',')
            if len(columns) < 11:
                return False, "", f"ERROR: Line {line_number} does not have enough columns. Expected at least 11, got {len(columns)}", 1
            
            # Extract parameters according to the specified order
            arg1 = columns[7].strip()   # coluna 8 (index 7)
            arg2 = columns[8].strip()   # coluna 9 (index 8)
            arg3 = columns[0].strip()   # coluna 1 (index 0)
            arg4 = columns[1].strip()   # coluna 2 (index 1)
            arg5 = columns[2].strip()   # coluna 3 (index 2)
            arg6 = columns[4].strip()   # coluna 5 (index 4)
            arg7 = columns[3].strip()   # coluna 4 (index 3)
            arg8 = columns[5].strip()   # coluna 6 (index 5)
            arg9 = columns[9].strip()   # coluna 10 (index 9)
            arg10 = columns[10].strip() # coluna 11 (index 10)
            
            print(f"Extracted parameters from line {line_number} of rates file:")
            print(f"  arg1 (col8): {arg1}")
            print(f"  arg2 (col9): {arg2}")
            print(f"  arg3 (col1): {arg3}")
            print(f"  arg4 (col2): {arg4}")
            print(f"  arg5 (col3): {arg5}")
            print(f"  arg6 (col5): {arg6}")
            print(f"  arg7 (col4): {arg7}")
            print(f"  arg8 (col6): {arg8}")
            print(f"  arg9 (col10): {arg9}")
            print(f"  arg10 (col11): {arg10}")

        # Build connection string and run sqlplus locally
        conn = f"{SQL_USERNAME}/{SQL_PASSWORD}@{SQL_DATABASE}"
        sql_dir = LOCAL_SQL.parent
        sql_file = LOCAL_SQL.name
        connection_string = f'cd "{sql_dir}" && sqlplus -s {conn} @{sql_file} {arg1} {arg2} {arg3} {arg4} {arg5} {arg6} {arg7} {arg8} {arg9} {arg10}'
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
        output_file = sql_dir / "generate_resumen_infos.csv"
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
    # Check if line number is provided as command line argument
    if len(sys.argv) < 2:
        print("ERROR: Please provide line number as argument")
        print("Usage: python generate_resumen_info.py <line_number>")
        print("Example: python generate_resumen_info.py 1")
        sys.exit(1)
    
    try:
        line_number = int(sys.argv[1])
        if line_number < 1:
            print("ERROR: Line number must be greater than 0")
            sys.exit(1)
    except ValueError:
        print("ERROR: Line number must be a valid integer")
        sys.exit(1)
    
    success, stdout, stderr, exit_code = generate_resumen_info(line_number)
    sys.exit(exit_code)
