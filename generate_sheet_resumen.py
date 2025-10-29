import os
import sys
import shutil
from pathlib import Path
from typing import Tuple, List
import xlrd
from xlutils.copy import copy
import xlwt
import logging
from datetime import datetime

def setup_logging():
    """
    Setup logging configuration to write errors to error_add_sheet.log file.
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'Logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    log_file = os.path.join(logs_dir, 'error_add_sheet.log')
    
    # Configure logging format with timestamp
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    return logging.getLogger(__name__)

def read_resumen_data(resumen_file: str) -> Tuple[bool, str, List[List[str]]]:
    """
    Read and parse the resumen.txt file.
    
    Args:
        resumen_file: Path to resumen.txt file
        
    Returns:
        Tuple[bool, str, List[List[str]]]: (success, error_message, parsed_data)
    """
    try:
        if not os.path.exists(resumen_file):
            return False, f"ERROR: resumen.txt file not found: {resumen_file}", []
        
        with open(resumen_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove empty lines and strip whitespace
        valid_lines = [line.strip() for line in lines if line.strip()]
        
        if not valid_lines:
            return False, "ERROR: resumen.txt file is empty", []
        
        # Parse CSV data
        parsed_data = []
        for line in valid_lines:
            # Split by comma and clean up whitespace
            row = [field.strip() for field in line.split(',')]
            parsed_data.append(row)
        
        # Remove duplicate rows based on all columns
        original_count = len(parsed_data)
        print(f"📋 Original data: {original_count} lines")
        unique_data = []
        seen_rows = set()
        
        for row in parsed_data:
            # Create a tuple of all values for comparison
            row_tuple = tuple(row)
            if row_tuple not in seen_rows:
                seen_rows.add(row_tuple)
                unique_data.append(row)
        
        print(f"📋 After removing duplicates: {len(unique_data)} lines")
        if original_count != len(unique_data):
            print(f"🗑️  Removed {original_count - len(unique_data)} duplicate lines")
        
        # Sort by FED (column 6) and time_premium (column 7) - assuming these are the date columns
        # FED appears to be column 6 (FECHA_INICIO) and time_premium column 7 (FECHA_FIN)
        def sort_key(row):
            if len(row) >= 8:
                # Extract date parts for sorting (assuming DD-MMM-YY format)
                try:
                    fed = row[6] if len(row) > 6 else ""
                    time_premium = row[7] if len(row) > 7 else ""
                    return (fed, time_premium)
                except:
                    return ("", "")
            return ("", "")
        
        unique_data.sort(key=sort_key)
        
        # Save cleaned data back to resumen.txt if duplicates were removed
        if original_count != len(unique_data):
            try:
                with open(resumen_file, 'w', encoding='utf-8') as f:
                    for row in unique_data:
                        f.write(','.join(row) + '\n')
                print(f"💾 Updated resumen.txt with cleaned data (removed duplicates)")
            except Exception as e:
                print(f"⚠️  Warning: Could not update resumen.txt file: {e}")
        
        parsed_data = unique_data
        
        return True, f"Successfully read and sorted {len(parsed_data)} lines from resumen.txt", parsed_data
        
    except Exception as e:
        return False, f"ERROR reading resumen.txt: {e}", []

def create_resumen_sheet(wb, parsed_data: List[List[str]]) -> None:
    """
    Create a new sheet with resumen data.
    
    Args:
        wb: Excel workbook object
        parsed_data: Parsed data from resumen.txt
    """
    # Create new sheet
    sheet = wb.add_sheet('Resumen', cell_overwrite_ok=True)
    
    # Define headers based on the data structure
    headers = [
        'IDD_CONCESION', 'IDD_OPERADOR', 'SERVICIO', 'PERIODO', 'TIPO_TARIFA', 'FECHA_INICIO', 
        'FECHA_FIN', 'TARIFA', 'VALOR', 'CANTIDAD'
    ]
    
    # Create header style
    header_style = xlwt.easyxf(
        'font: bold True, color black; '
        'pattern: pattern solid, fore_colour light_blue; '
        'borders: left thin, right thin, top thin, bottom thin; '
        'align: horiz center, vert center'
    )
    
    # Create data style
    data_style = xlwt.easyxf(
        'borders: left thin, right thin, top thin, bottom thin; '
        'align: vert center'
    )
    
    # Write headers
    for col, header in enumerate(headers):
        sheet.write(0, col, header, header_style)
    
    # Write data
    for row_idx, row_data in enumerate(parsed_data, start=1):
        for col_idx, value in enumerate(row_data):
            if col_idx < len(headers):  # Ensure we don't exceed header count
                sheet.write(row_idx, col_idx, value, data_style)
    
    # Set appropriate column widths to ensure visibility
    column_widths = [
        2000,  # IDD_CONCESION
        2000,  # IDD_OPERADOR
        3000,  # SERVICIO
        2000,  # PERIODO
        2000,  # TIPO_TARIFA
        2500,  # FECHA_INICIO
        2500,  # FECHA_FIN
        2000,  # TARIFA
        3000,  # VALOR
        2000   # CANTIDAD
    ]
    
    for col, width in enumerate(column_widths):
        sheet.col(col).width = width

def generate_sheet_resumen(xls_file_path: str) -> Tuple[bool, str]:
    """
    Generate a new sheet in the Excel file with resumen data.
    
    Args:
        xls_file_path: Path to the original Excel file
        
    Returns:
        Tuple[bool, str]: (success, error_message)
    """
    logger = setup_logging()
    
    try:
        # Validate input file
        if not os.path.exists(xls_file_path):
            return False, f"ERROR: Excel file not found: {xls_file_path}"
        
        # Read resumen data
        resumen_file = os.path.join(os.path.dirname(__file__), 'resumen.txt')
        success, message, parsed_data = read_resumen_data(resumen_file)
        
        if not success:
            return False, message
        
        print(f"📊 {message}")
        
        # Get filename for backup operations
        filename = os.path.basename(xls_file_path)
        
        # Create backup directory
        backup_dir = os.path.join(os.path.dirname(__file__), 'Backup_files')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Check if Resumen sheet already exists first
        rb_check = xlrd.open_workbook(xls_file_path, formatting_info=True)
        sheet_names = [sheet.name for sheet in rb_check.sheets()]
        
        if 'Resumen' in sheet_names:
            print("⚠️  Sheet 'Resumen' already exists. Creating backup and removing Resumen sheet...")
            # Create backup with same name as original file (with Resumen)
            backup_file = os.path.join(backup_dir, filename)
            shutil.copy2(xls_file_path, backup_file)
            print(f"💾 Backup created: {backup_file}")
            
            # Create new workbook with only original sheets (excluding Resumen)
            new_wb = xlwt.Workbook()
            for sheet in rb_check.sheets():
                if sheet.name != 'Resumen':
                    # Copy sheet data to new workbook
                    new_sheet = new_wb.add_sheet(sheet.name)
                    for row in range(sheet.nrows):
                        for col in range(sheet.ncols):
                            try:
                                cell_value = sheet.cell(row, col).value
                                new_sheet.write(row, col, cell_value)
                            except:
                                pass
            
            # Save the new workbook
            new_wb.save(xls_file_path)
            print("📄 Created new workbook without Resumen sheet")
        else:
            # No Resumen sheet exists, create backup of original file
            backup_file = os.path.join(backup_dir, filename)
            shutil.copy2(xls_file_path, backup_file)
            print(f"💾 Backup created: {backup_file}")
        
        # Open workbook
        print(f"📖 Opening Excel file: {xls_file_path}")
        rb = xlrd.open_workbook(xls_file_path, formatting_info=True)
        wb = copy(rb)
        
        # Create resumen sheet
        print("📝 Creating Resumen sheet...")
        create_resumen_sheet(wb, parsed_data)
        
        # Save the workbook
        print("💾 Saving Excel file...")
        wb.save(xls_file_path)
        
        print(f"✅ Successfully added Resumen sheet to {filename}")
        print(f"📊 Added {len(parsed_data)} data rows to the sheet")
        
        return True, f"Successfully added Resumen sheet with {len(parsed_data)} rows"
        
    except Exception as e:
        error_msg = f"ERROR: {e}"
        logger.error(error_msg)
        return False, error_msg

if __name__ == "__main__":
    # Check if file path is provided as command line argument
    if len(sys.argv) < 2:
        print("ERROR: Please provide Excel file path as argument")
        print("Usage: python generate_sheet_resumen.py <excel_file_path>")
        print("Example: python generate_sheet_resumen.py ./Liquidation_files/317_114_AIRTIME_TECHNOLOGIES_CHILE_SPA_202509_TALT_R_I_20251008_182417.xls")
        sys.exit(1)
    
    xls_file_path = sys.argv[1]
    
    print("🚀 Starting resumen sheet generation...")
    success, message = generate_sheet_resumen(xls_file_path)
    
    if success:
        print(f"\n🎉 {message}")
        sys.exit(0)
    else:
        print(f"\n❌ {message}")
        sys.exit(1)
