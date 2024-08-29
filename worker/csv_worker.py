import asyncio
from repository.db_ops import db_ops
import csv

async def process_image(url, product_name):
    await asyncio.sleep(2)
    return "aa"

async def process_csv(csv_data,req_id):
    tasks = []
    reader = csv.DictReader(csv_data.splitlines())
    for row_number,row in enumerate(reader,start=1):
        try:
            serial_number = row.get('S. No.')
            product_name = row.get('Product Name')
            input_urls_string = row.get('Input Image Urls')
            input_urls = [url.strip('"').strip() for url in input_urls_string.split(',')]


            for url in input_urls:
                tasks.append(process_image(url,product_name))

            output_urls = asyncio.gather(*tasks)

            output_urls = [url for url in output_urls if url is not None]

            print(output_urls)
            await db_ops.jobs.update_one({"requestId": req_id}, {"$set": {"status": "completed"}})

        except Exception as err:
            print(err)
            pass

