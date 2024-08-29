import asyncio
from repository.db_ops import db_ops
import csv
import aiohttp
from PIL import Image
import io
from config.digi_ocean_config import do_client

async def process_image(url, req_id,product_name):
     async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            image_data = await response.read()
        
        img = Image.open(io.BytesIO(image_data))
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=50)
        output.seek(0)

        file_name = f"output_compressed_{url.split('/')[-1]}"
        bucket_name = "imagecompress211"  # Replace with your actual bucket name
        object_name = f"compressed_images/{req_id}/{product_name}/{file_name}"
        try:
            # Upload the compressed image to DigitalOcean Spaces
            do_client.upload_fileobj(output, bucket_name, object_name)
            print(f"File uploaded successfully to {bucket_name}/{object_name}")
        except Exception as e:
            print(f"Failed to upload file to DigitalOcean Spaces: {e}")
            return None


async def process_csv(csv_data,req_id):
    reader = csv.DictReader(csv_data.splitlines())
    results = []
    for row in reader:
        try:
            serial_number = row.get('S. No.')
            product_name = row.get('Product Name')
            input_urls_string = row.get('Input Image Urls')
            input_urls = [url.strip('"').strip() for url in input_urls_string.split(',')]

            tasks = []
            for url in input_urls:
                tasks.append(process_image(url,req_id,product_name))

            output_urls = await asyncio.gather(*tasks)

            output_urls = [url for url in output_urls if url is not None]

            print(output_urls)

            results.append({
            "serialNumber": serial_number,
            "productName": product_name,
            "inputImageUrls": input_urls,
            "outputImageUrls": output_urls
            })

        except Exception as err:
            print(err)
            pass
    await db_ops.update_job_status(req_id,"Completed")
    # await db_ops.insert_product({req_id: results})
