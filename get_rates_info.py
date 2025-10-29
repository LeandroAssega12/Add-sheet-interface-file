import os
import sys
from pathlib import Path
import subprocess
from dotenv import load_dotenv
from typing import Tuple, Optional, List

# Load .env
ENV_PATH = Path(__file__).parent / "config" / ".env"
if ENV_PATH.exists():
    load_dotenv(str(ENV_PATH))

def get_args_info(filename: str) -> Tuple[bool, str, List[str]]:
    """
    Extract parameters from filename for SQL execution.
    
    Args:
        filename: File name like "317_114_AIRTIME_TECHNOLOGIES_CHILE_SPA_202509_TALT_R_I_20251008_182417.xls"
                 Will extract 5 parameters by splitting on "_"
        
    Returns:
        Tuple[bool, str, List[str]]: (success, error_message, [arg1, arg2, arg3, arg4, arg5])
    """
    # First, check if any rating component from rating_component_list.csv is found in filename
    rating_component_file = Path(__file__).parent / "SQL_files" / "rating_component_list.csv"
    
    if not rating_component_file.exists():
        return False, f"ERROR: Rating component list file not found: {rating_component_file}", []
    
    try:
        # Read rating components from file
        with open(rating_component_file, 'r', encoding='utf-8') as f:
            rating_components = [line.strip() for line in f.readlines() if line.strip()]
        
        # Find matching rating component in filename
        found_component = None
        for component in rating_components:
            if component in filename:
                found_component = component
                break
        
        # Count underscores in the found component (or 0 if not found)
        if found_component:
            rat_comp_underscore = found_component.count('_')
            print(f"Found rating component '{found_component}' in filename with {rat_comp_underscore} underscores")
        else:
            rat_comp_underscore = 0
            print(f"No valid rating component found in filename '{filename}'. Will use parts[3] + extra_args for arg4")
        
    except Exception as e:
        return False, f"ERROR: Could not read rating component list: {e}", []
    
    # Extract parameters from filename by splitting on "_"
    parts = filename.split("_")
    
    if len(parts) < 5:
        return False, f"ERROR: Filename must have at least 5 parts separated by '_'. Got {len(parts)} parts: {parts}", []
    
    # Extract the 5 required parameters
    extra_args = len(parts) - 8 - rat_comp_underscore #check if the filename has more than 8 parts
    arg1 = parts[0]  # fk_orga_fran (franchise)
    arg2 = parts[1]  # fk_orga_oper (operator)
    arg3 = parts[2+extra_args]  # name (period) - will be the third part
    arg4 = found_component if found_component else parts[3+extra_args]  # rating_component - use found component or parts[3]+extra_args
    arg5 = parts[5+extra_args+rat_comp_underscore] if found_component else parts[5+extra_args]  # component_direction - will be the fifth part
    
    print(f"Extracted parameters from filename '{filename}':")
    print(f"  arg1 (franchise): {arg1}")
    print(f"  arg2 (operator): {arg2}")
    print(f"  arg3 (period): {arg3}")
    print(f"  arg4 (rating_component): {arg4}")
    print(f"  arg5 (component_direction): {arg5}")
    print(f"  rat_comp_underscore: {rat_comp_underscore}")
    
    return True, "", [arg1, arg2, arg3, arg4, arg5]

def get_rates_info(filename: str) -> Tuple[bool, str, str, int]:
    """
    Execute rates info search by extracting parameters from filename.
    
    Args:
        filename: File name like "317_114_AIRTIME_TECHNOLOGIES_CHILE_SPA_202509_TALT_R_I_20251008_182417.xls"
                 Will extract 5 parameters by splitting on "_"
        
    Returns:
        Tuple[bool, str, str, int]: (success, stdout, stderr, exit_code)
    """
    # Extract parameters from filename
    success, error_msg, args = get_args_info(filename)
    if not success:
        return False, "", error_msg, 1
    
    arg1, arg2, arg3, arg4, arg5 = args
    # Read DB connection parts (user/password@ALIAS_TNS)
    SQL_USERNAME = os.getenv("SQL_USERNAME")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_DATABASE = os.getenv("SQL_DATABASE")

    # Validate required vars
    if not SQL_USERNAME or not SQL_PASSWORD or not SQL_DATABASE:
        return False, "", "ERROR: Set SQL_USERNAME, SQL_PASSWORD and SQL_DATABASE in config/.env", 1

    # Paths
    LOCAL_SQL = Path(__file__).parent / "SQL_files" / "rates_info_search.sql"

    if not LOCAL_SQL.exists():
        return False, "", f"ERROR: Local SQL not found: {LOCAL_SQL}", 1

    try:
        # Build connection string and run sqlplus locally
        conn = f"{SQL_USERNAME}/{SQL_PASSWORD}@{SQL_DATABASE}"
        sql_dir = LOCAL_SQL.parent
        sql_file = LOCAL_SQL.name
        connection_string = f'cd "{sql_dir}" && sqlplus -s {conn} @{sql_file} {arg1} {arg2} {arg3} {arg4} {arg5}'
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
        output_file = sql_dir / "rates_info_search.csv"
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
    # Check if filename is provided as command line argument
    if len(sys.argv) < 2:
        print("ERROR: Please provide filename as argument")
        print("Usage: python get_rates_info.py <filename>")
        print("Example: python get_rates_info.py 317_114_AIRTIME_TECHNOLOGIES_CHILE_SPA_202509_TALT_R_I_20251008_182417.xls")
        sys.exit(1)
    
    filename = sys.argv[1]
    success, stdout, stderr, exit_code = get_rates_info(filename)
    sys.exit(exit_code)
