# Add Sheet Interface v2

A Python automation tool for processing Excel files and generating summary sheets with billing information. This tool integrates with Oracle databases to extract billing data and automatically adds a "Resumen" sheet to Excel files with processed information.

## 🚀 Features

- **Automated Excel Processing**: Processes multiple Excel files in batch
- **Database Integration**: Connects to Oracle databases using SQL*Plus
- **Resumen Sheet Generation**: Automatically adds a summary sheet to Excel files
- **Duplicate Detection**: Removes duplicate entries before processing
- **Data Sorting**: Sorts data by date columns (FED and time_premium)
- **Backup Management**: Creates automatic backups before modifications
- **Error Handling**: Comprehensive logging and error management

## 📋 Requirements

- Python 3.7+
- Oracle SQL*Plus client
- Windows PowerShell (for script execution)
- Oracle database access credentials

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/LeandroAssega12/Add-sheet-interface-file.git
cd Add-sheet-interface-file
```

### 2. Setup Virtual Environment
```powershell
.\setup_venv.ps1
```

### 3. Configure Database Connection
Create a `.env` file in the `config/` directory:
```env
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
SQL_DATABASE=your_database_alias
```

## 🚀 Usage

### Basic Usage
```powershell
# Process all Excel files in a directory
.\run.ps1 -DataDir ".\Liquidation_files"

# Or run directly with Python
python main.py ".\Liquidation_files"
```

### Individual Script Usage

#### Process Rating Components
```bash
python generate_rating_component_list.py
```

#### Get Rates Information
```bash
python get_rates_info.py "filename.xls"
```

#### Generate Resumen Sheet
```bash
python generate_sheet_resumen.py "path\to\file.xls"
```

## 📁 Project Structure

```
Add-sheet-interface-file/
├── main.py                          # Main entry point
├── generate_sheet_resumen.py        # Resumen sheet generation
├── generate_resumen_info.py         # Resumen information processing
├── generate_rating_component_list.py # Rating component list generation
├── get_rates_info.py                # Rates information extraction
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── .gitignore                       # Git ignore rules
├── SQL_files/                       # SQL scripts
│   ├── generate_resumen_infos.sql
│   ├── rates_info_search.sql
│   └── rating_component_list.sql
├── Utils/                          # Utility modules
│   ├── logging_setup.py
│   └── table_styles.py
├── config/                         # Configuration files
│   └── settings.json
├── layouts/                        # Layout processors
└── Backup_files/                   # Automatic backups
```

## 🔧 Configuration

### Database Settings
Configure your Oracle database connection in `config/.env`:
```env
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
SQL_DATABASE=your_database_alias
```

### Excel File Naming Convention
The tool expects Excel files with the following naming pattern:
```
{IDD_CONCESION}_{IDD_OPERADOR}_{COMPANY_NAME}_{PERIOD}_{RATING_COMPONENT}_{DIRECTION}_{TIMESTAMP}.xls
```

Example: `317_114_AIRTIME_TECHNOLOGIES_CHILE_SPA_202509_TALT_R_I_20251008_182417.xls`

## 📊 Output

The tool generates:
- **Resumen Sheet**: A new sheet in each Excel file containing:
  - IDD_CONCESION
  - IDD_OPERADOR
  - SERVICIO
  - PERIODO
  - TIPO_TARIFA
  - FECHA_INICIO
  - FECHA_FIN
  - TARIFA
  - VALOR
  - CANTIDAD

- **Backup Files**: Original files are backed up in `Backup_files/` directory
- **Logs**: Processing logs are saved in `Logs/` directory

## 🔄 Workflow

1. **Update Rating Components**: Executes `generate_rating_component_list.py`
2. **Process Each Excel File**:
   - Extract parameters from filename
   - Query database for rates information
   - Generate resumen data for each rate
   - Remove duplicates and sort data
   - Add Resumen sheet to Excel file
3. **Create Backups**: Automatic backup creation before modifications

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify credentials in `config/.env`
   - Ensure SQL*Plus is installed and accessible
   - Check database connectivity

2. **Excel File Not Found**
   - Verify file path and naming convention
   - Check file permissions

3. **Permission Errors**
   - Run PowerShell as Administrator
   - Check file write permissions

### Logs
Check the `Logs/` directory for detailed error information:
- `app.log`: General application logs
- `error_add_sheet.log`: Excel processing errors

## 📝 Dependencies

- `paramiko==3.4.0`: SSH connections
- `python-dotenv==1.0.1`: Environment variable management
- `xlrd==2.0.1`: Excel file reading
- `xlwt==1.3.0`: Excel file writing
- `xlutils==2.0.0`: Excel file utilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Author

**Leandro Assega**
- GitHub: [@LeandroAssega12](https://github.com/LeandroAssega12)

## 📞 Support

For support and questions, please open an issue in the GitHub repository.