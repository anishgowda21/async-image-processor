import aiofiles
import asyncio
import csv
from urllib.parse import urlparse 
from My_Exception.custom_exception import CustomException



async def validate_csv(csv_file):

    if not csv_file.filename.endswith(".csv"):
        raise CustomException("Please Upload a CSV file")

    content = await csv_file.read()
    content = content.decode('utf-8')

    reader = csv.DictReader(content.splitlines())

    required_columns = ['Serial Number', 'Product Name', 'Input Image Urls']

    if required_columns != (reader.fieldnames):
        raise CustomException(f"Missing columns. Required columns are: {required_columns}")

    for row_number,row in enumerate(reader,start=1):
        if len(row) != 3:
            raise CustomException(f"Row {row_number}: Invalid number of columns")
        
        serial_number = row.get('Serial Number')
        product_name = row.get('Product Name')
        input_image_urls = row.get('Input Image Urls')
        
        if not serial_number.isdigit():
            raise CustomException(f"Invalid Serial Number at row {row_number}: {serial_number}")
        
        # Validate Product Name
        if not product_name or not isinstance(product_name, str) or not product_name.strip():
            raise CustomException(f"Invalid Product Name at row {row_number}: {product_name}")
        
        # Validate Input Image Urls
        if not input_image_urls or not isinstance(input_image_urls, str):
            raise CustomException(f"Invalid Input Image Urls at row {row_number}: {input_image_urls}")

        
        for url in input_image_urls.split(','):
            url = url.strip('"').strip() 
            if not url.startswith(('http://', 'https://')):
                raise CustomException(f"Row {row_number}: Invalid URL format: {url}")

        
        message = "Valid CSV"

    return content

