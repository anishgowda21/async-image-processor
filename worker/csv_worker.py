import asyncio

async def process_csv(csv_data,req_id):
    for row in csv_data:
        try:
            serial_number, product_name, input_urls_string = row
            input_urls = [url.strip('"').strip() for url in input_urls_string.split(',')]
            output_urls = []

            
        except Exception as err:
            pass

