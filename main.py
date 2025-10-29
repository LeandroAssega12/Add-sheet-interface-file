import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
import glob

# Import the functions from other modules
from generate_rating_component_list import generate_rating_component_list
from get_rates_info import get_rates_info
from generate_resumen_info import generate_resumen_info
from generate_sheet_resumen import generate_sheet_resumen

def process_directory(directory_path: str) -> Tuple[bool, str]:
    """
    Process all .xls files in the specified directory.
    
    Args:
        directory_path: Path to directory containing .xls files
        
    Returns:
        Tuple[bool, str]: (success, error_message)
    """
    # Convert to Path object
    dir_path = Path(directory_path)
    
    # Validate directory exists
    if not dir_path.exists():
        return False, f"ERROR: Directory does not exist: {directory_path}"
    
    if not dir_path.is_dir():
        return False, f"ERROR: Path is not a directory: {directory_path}"
    
    try:
        print(f"🔄 Processing directory: {directory_path}")
        
        # Step 1: Update rating component list
        print("\n📋 Step 1: Updating rating component list...")
        success, stdout, stderr, exit_code = generate_rating_component_list()
        if not success:
            return False, f"ERROR: Failed to update rating component list: {stderr}"
        print("✅ Rating component list updated successfully!")
        
        # Step 2: Find all .xls files in directory
        print(f"\n📁 Step 2: Finding .xls files in {directory_path}...")
        xls_files = list(dir_path.glob("*.xls"))
        
        if not xls_files:
            return False, f"ERROR: No .xls files found in directory: {directory_path}"
        
        print(f"✅ Found {len(xls_files)} .xls files:")
        for file in xls_files:
            print(f"  - {file.name}")
        
        # Step 3: Process each .xls file individually
        print(f"\n🔄 Step 3: Processing .xls files...")
        processed_files = []
        
        for xls_file in xls_files:
            print(f"\n📄 Processing file: {xls_file.name}")
            
            # Step 3a: Get rates info for this file
            success, stdout, stderr, exit_code = get_rates_info(xls_file.name)
            
            if not success:
                print(f"❌ Error processing file {xls_file.name}: {stderr}")
                continue
            
            print(f"✅ File {xls_file.name} processed successfully!")
            
            # Step 3b: Process rates_info_search.csv and generate resumen.txt for this file
            print(f"📊 Generating resumen.txt for {xls_file.name}...")
            
            rates_file = Path(__file__).parent / "SQL_files" / "rates_info_search.csv"
            resumen_file = Path(__file__).parent / "resumen.txt"
            
            if not rates_file.exists():
                print(f"❌ rates_info_search.csv not found for {xls_file.name}")
                continue
            
            # Read rates_info_search.csv to get number of lines
            with open(rates_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Remove empty lines
            valid_lines = [line for line in lines if line.strip()]
            
            if not valid_lines:
                print(f"❌ rates_info_search.csv is empty for {xls_file.name}")
                continue
            
            print(f"📋 Found {len(valid_lines)} lines in rates_info_search.csv")
            
            # Process each line and write to resumen.txt
            resumen_content = []
            
            for line_num in range(1, len(valid_lines) + 1):
                print(f"  Processing line {line_num}...")
                
                success, stdout, stderr, exit_code = generate_resumen_info(line_num)
                
                if success:
                    # Read the generated output from generate_resumen_infos.csv
                    resumen_csv = Path(__file__).parent / "SQL_files" / "generate_resumen_infos.csv"
                    if resumen_csv.exists():
                        with open(resumen_csv, 'r', encoding='utf-8') as f:
                            csv_content = f.read().strip()
                            if csv_content:
                                resumen_content.append(csv_content)
                                print(f"    ✅ Line {line_num} processed successfully")
                            else:
                                print(f"    ⚠️  Line {line_num} generated empty content")
                    else:
                        print(f"    ⚠️  Line {line_num} - generate_resumen_infos.csv not found")
                else:
                    print(f"    ❌ Error processing line {line_num}: {stderr}")
            
            # Write resumen.txt
            if resumen_content:
                with open(resumen_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(resumen_content))
                
                print(f"✅ resumen.txt generated successfully for {xls_file.name}!")
                print(f"📊 Total lines processed: {len(resumen_content)}")
                
                # Step 3c: Generate Resumen sheet in the Excel file
                print(f"📝 Adding Resumen sheet to {xls_file.name}...")
                success, message = generate_sheet_resumen(str(xls_file))
                
                if success:
                    print(f"✅ {message}")
                    processed_files.append(xls_file.name)
                else:
                    print(f"❌ Error adding Resumen sheet to {xls_file.name}: {message}")
            else:
                print(f"❌ No content was generated for resumen.txt for {xls_file.name}")
        
        if not processed_files:
            return False, "ERROR: No files were processed successfully"
        
        return True, f"Successfully processed {len(processed_files)} files with Resumen sheets"
        
    except Exception as e:
        return False, f"ERROR: {e}"

if __name__ == "__main__":
    # Check if directory path is provided as command line argument
    if len(sys.argv) < 2:
        print("ERROR: Please provide directory path as argument")
        print("Usage: python main.py <directory_path>")
        print("Example: python main.py C:\\path\\to\\xls\\files")
        print("         python main.py ./Liquidation_files")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    print("🚀 Starting main processing...")
    success, message = process_directory(directory_path)
    
    if success:
        print(f"\n🎉 {message}")
        sys.exit(0)
    else:
        print(f"\n❌ {message}")
        sys.exit(1)
