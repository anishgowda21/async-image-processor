import asyncio
from repository.db_ops import db_ops
import csv
import aiohttp
from PIL import Image,UnidentifiedImageError
import urllib.parse
import io
from config.digi_ocean_config import upload,ENDPOINT_URL

async def process_image(url, req_id, product_name):
    file_name = f"output_compressed_{url.split('/')[-1]}"
    bucket_name = "compressed_images"
    object_name = f"{req_id}/{product_name}/{file_name}"

    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f"Failed to fetch image from {url}. Status: {response.status}")
                        return None
                    image_data = await response.read()
            except aiohttp.ClientError as e:
                print(f"HTTP error occurred while fetching {url}: {e}")
                return None

        try:
            img = Image.open(io.BytesIO(image_data))
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=50)
            output.seek(0)
        except UnidentifiedImageError:
            print(f"Failed to process image from {url}: Unidentified image format")
            return None

        try:
            await upload(output, bucket_name, object_name)
            encoded_object_name = urllib.parse.quote(object_name)
            return f"{ENDPOINT_URL}/{bucket_name}/{encoded_object_name}"
        except Exception as e:
            print(f"Failed to upload file for {url}: {e}")
            return None
    except Exception as e:
        print(f"Unexpected error processing {url}: {e}")
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
    await db_ops.insert_product({req_id: results})
