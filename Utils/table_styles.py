import xlwt

def create_table_styles():
    """Create and return table styles for headers and data cells"""
    # Create styles for table formatting
    header_style = xlwt.XFStyle()
    header_font = xlwt.Font()
    header_font.bold = True
    header_font.height = 220  # Font size
    header_style.font = header_font
    
    # Add borders to header style
    header_borders = xlwt.Borders()
    header_borders.left = xlwt.Borders.THIN
    header_borders.right = xlwt.Borders.THIN
    header_borders.top = xlwt.Borders.THIN
    header_borders.bottom = xlwt.Borders.THIN
    header_style.borders = header_borders
    
    # Add background color to header
    header_pattern = xlwt.Pattern()
    header_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    header_pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
    header_style.pattern = header_pattern
    
    # Create style for data cells
    data_style = xlwt.XFStyle()
    data_borders = xlwt.Borders()
    data_borders.left = xlwt.Borders.THIN
    data_borders.right = xlwt.Borders.THIN
    data_borders.top = xlwt.Borders.THIN
    data_borders.bottom = xlwt.Borders.THIN
    data_style.borders = data_borders
    
    return header_style, data_style 