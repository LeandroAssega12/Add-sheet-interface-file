import xlrd
from xlutils.copy import copy
import xlwt
import shutil
import os
import json
import logging
from datetime import datetime
from Utils.table_styles import create_table_styles

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

def extract_filename_data(filename):
    """
    Extract data from filename based on the expected format.
    
    Args:
        filename (str): The filename to parse
        
    Returns:
        dict: Dictionary containing extracted data
    """
    filename_parts = filename.split('_')
    
    if len(filename_parts) < 8:
        raise ValueError(f"The filename format is not valid, please check README.md file for the correct format: {filename}")
    
    return {
        'IDD_CONCESION': filename_parts[1],
        'IDD_OPERADOR': filename_parts[0],
        'PERIODO': filename_parts[3],
        'SERVICIO': filename_parts[4]
    }

def find_subtotal_values(sheet):
    """
    Find MENSAJES1 and MENSAJES2 by locating the first two occurrences of "SUBTOTAL"
    and taking the value 4 cells ahead.
    
    Args:
        sheet: Excel sheet object
        
    Returns:
        tuple: (MENSAJES1, MENSAJES2)
    """
    mensajes1 = None
    mensajes2 = None
    subtotal_count = 0
    
    for row_idx in range(sheet.nrows):
        for col_idx in range(sheet.ncols):
            cell_value = str(sheet.cell_value(row_idx, col_idx)).strip()
            if cell_value == "SUBTOTAL":
                subtotal_count += 1
                if subtotal_count == 1:
                    # First occurrence - get value 4 cells ahead
                    if col_idx + 4 < sheet.ncols:
                        mensajes1 = sheet.cell_value(row_idx, col_idx + 4)
                elif subtotal_count == 2:
                    # Second occurrence - get value 4 cells ahead
                    if col_idx + 4 < sheet.ncols:
                        mensajes2 = sheet.cell_value(row_idx, col_idx + 4)
                    break
    
    if mensajes1 is None or mensajes2 is None:
        raise ValueError("Could not find two occurrences of 'SUBTOTAL' in the sheet")
    
    return mensajes1, mensajes2

def layout_317(arquivo, modelo):
    """
    Add a resume sheet to an Excel file based on the 317 model.
    
    Args:
        arquivo (str): Path to the Excel file
        modelo (str): Model name (should be '317')
    """
    # Setup logging
    logger = setup_logging()
    
    try:
        # Extract data from filename
        filename = os.path.basename(arquivo)
        filename_data = extract_filename_data(filename)
        print(f"Extracted from filename - IDD_CONCESION: {filename_data['IDD_CONCESION']}, "
              f"IDD_OPERADOR: {filename_data['IDD_OPERADOR']}, "
              f"PERIODO: {filename_data['PERIODO']}, "
              f"SERVICIO: {filename_data['SERVICIO']}")
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), 'layout_models', 'model_317.json')
        with open(config_path, 'r') as f:
            model_config = json.load(f)
        
        if modelo not in model_config:
            raise ValueError(f"Model '{modelo}' not found in configuration file")
        
        model_fields = model_config[modelo]
        
        # Create backup in Backup_files directory
        backup_dir = os.path.join(os.path.dirname(__file__), 'Backup_files')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        filename = os.path.basename(arquivo)
        backup_filename = filename.replace('.xls', '_backup.xls').replace('.xlsx', '_backup.xlsx')
        backup_file = os.path.join(backup_dir, backup_filename)
        shutil.copy2(arquivo, backup_file)
        print(f"Backup created: {backup_file}")
        
        # Open workbook
        rb = xlrd.open_workbook(arquivo, formatting_info=True)
        wb = copy(rb)
        
        # Check if sheet already exists
        sheet_names = [sheet.name for sheet in rb.sheets()]
        if 'NovaAba' in sheet_names:
            print("Sheet 'NovaAba' already exists. Skipping.")
            return
        
        # Add new sheet
        nova_aba = wb.add_sheet('NovaAba')
        
        # Create styles
        header_style, data_style = create_table_styles()
        
        # Define headers
        headers = ["IDD_CONCESION", "IDD_OPERADOR", "Servicio", "Periodo", "Mensajes", "Monto", "Tramo_Tarifario", "Descripcion_tramo_tarifario"]
        
        # Write headers
        for col_num, header in enumerate(headers):
            nova_aba.write(0, col_num, header, header_style)
        
        # Read data from first sheet
        first_sheet = rb.sheet_by_index(0)
        
        # Find MENSAJES1 and MENSAJES2 dynamically
        MENSAJES1, MENSAJES2 = find_subtotal_values(first_sheet)
        print(f"Found MENSAJES1: {MENSAJES1}, MENSAJES2: {MENSAJES2}")
        
        # Read monetary and tariff values
        MONTO1 = float(str(first_sheet.cell_value(model_fields["MONTO1"]["row"], model_fields["MONTO1"]["col"])).replace('$', '').replace('.', ''))
        MONTO2 = float(str(first_sheet.cell_value(model_fields["MONTO2"]["row"], model_fields["MONTO2"]["col"])).replace('$', '').replace('.', ''))
        TARIFA1 = float(str(first_sheet.cell_value(model_fields["TARIFA1"]["row"], model_fields["TARIFA1"]["col"])).replace('$', '').replace(',', '.'))
        TARIFA2 = float(str(first_sheet.cell_value(model_fields["TARIFA2"]["row"], model_fields["TARIFA2"]["col"])).replace('$', '').replace(',', '.'))
        
        # Read other values
        DESCRIPCION1 = first_sheet.cell_value(model_fields["DESCRIPCION_TRAMO_TARIFARIO1"]["row"], model_fields["DESCRIPCION_TRAMO_TARIFARIO1"]["col"])
        DESCRIPCION2 = first_sheet.cell_value(model_fields["DESCRIPCION_TRAMO_TARIFARIO2"]["row"], model_fields["DESCRIPCION_TRAMO_TARIFARIO2"]["col"])
        
        # Write first row
        nova_aba.write(1, 0, filename_data['IDD_CONCESION'], data_style)
        nova_aba.write(1, 1, filename_data['IDD_OPERADOR'], data_style)
        nova_aba.write(1, 2, filename_data['SERVICIO'], data_style)
        nova_aba.write(1, 3, filename_data['PERIODO'], data_style)
        nova_aba.write(1, 4, MENSAJES1, data_style)
        nova_aba.write(1, 5, MONTO1, data_style)
        nova_aba.write(1, 6, TARIFA1, data_style)
        nova_aba.write(1, 7, DESCRIPCION1, data_style)
        
        # Write second row
        nova_aba.write(2, 0, filename_data['IDD_CONCESION'], data_style)
        nova_aba.write(2, 1, filename_data['IDD_OPERADOR'], data_style)
        nova_aba.write(2, 2, filename_data['SERVICIO'], data_style)
        nova_aba.write(2, 3, filename_data['PERIODO'], data_style)
        nova_aba.write(2, 4, MENSAJES2, data_style)
        nova_aba.write(2, 5, MONTO2, data_style)
        nova_aba.write(2, 6, TARIFA2, data_style)
        nova_aba.write(2, 7, DESCRIPCION2, data_style)
        
        # Auto-adjust column widths
        for col_num in range(len(headers)):
            max_width = 0
            
            # Check header width
            header_width = len(str(headers[col_num])) * 256
            max_width = max(max_width, header_width)
            
            # Check data width for first row
            data_values = [filename_data['IDD_CONCESION'], filename_data['IDD_OPERADOR'], 
                          filename_data['SERVICIO'], filename_data['PERIODO'], 
                          MENSAJES1, MONTO1, TARIFA1, DESCRIPCION1]
            
            if col_num < len(data_values):
                data_width = len(str(data_values[col_num])) * 256
                max_width = max(max_width, data_width)
            
            # Set minimum width and add padding
            min_width = 10 * 256
            final_width = max(max_width + 512, min_width)
            
            nova_aba.col(col_num).width = final_width
        
        # Save the modified file
        wb.save(arquivo)
        print("New sheet 'NovaAba' added successfully!")
        
        # Verify the original sheet is intact
        rb_verify = xlrd.open_workbook(arquivo)
        print(f"File now contains {len(rb_verify.sheets())} sheets: {[sheet.name for sheet in rb_verify.sheets()]}")
        
    except Exception as e:
        # Log the error with timestamp
        error_message = f"Error processing file '{arquivo}' with model '{modelo}': {str(e)}"
        logger.error(error_message)
        
        # Also print to console for immediate feedback
        print(f"Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        
        # Restore from backup if it exists
        if 'backup_file' in locals():
            print("Restoring from backup...")
            shutil.copy2(backup_file, arquivo)
            print("Original file restored.")

# Example usage
if __name__ == "__main__":
    arquivo = '317_225_WOM_S.A._202505_TBAJ_R_I_20250607_232028.xls'
    modelo = '317'
    layout_317(arquivo, modelo) 