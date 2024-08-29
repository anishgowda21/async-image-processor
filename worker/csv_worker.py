import asyncio
from repository.db_ops import db_ops
import csv
import aiohttp
from PIL import Image, UnidentifiedImageError
import urllib.parse
import io
from config.digi_ocean_config import upload, ENDPOINT_URL

async def process_image(url, req_id, product_name):
    file_name = f"output_compressed_{url.split('/')[-1]}"
    bucket_name = "compressed_images"
    object_name = f"{req_id}/{product_name}/{file_name}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"Failed to fetch image. Status: {response.status}")
                image_data = await response.read()

        img = Image.open(io.BytesIO(image_data))
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=50)
        output.seek(0)

        await upload(output, bucket_name, object_name)
        encoded_object_name = urllib.parse.quote(object_name)
        return f"{ENDPOINT_URL}/{bucket_name}/{encoded_object_name}"
    except aiohttp.ClientError as e:
        print(f"HTTP error occurred while fetching {url}: {e}")
    except UnidentifiedImageError:
        print(f"Failed to process image from {url}: Unidentified image format")
    except Exception as e:
        print(f"Unexpected error processing {url}: {e}")
    return None

async def save_results_to_csv(results, req_id):
    output_csv = io.StringIO()
    fieldnames = ["S. No.", "Product Name", "Input Image Urls", "Output Image Urls"]
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow({
            "S. No.": row["S. No."],
            "Product Name": row["Product Name"],
            "Input Image Urls": f"\"{','.join(row['Input Image Urls'])}\"",
            "Output Image Urls": f"\"{','.join(row['Output Image Urls'])}\""
        })
    csv_data = output_csv.getvalue().encode('utf-8')
    csv_bytes = io.BytesIO(csv_data)

    bucket_name = "outputcsv"
    object_name = f"{req_id}/res_file.csv"
    try:
        await upload(csv_bytes, bucket_name, object_name)
        csv_url = f"{ENDPOINT_URL}/{bucket_name}/{urllib.parse.quote(object_name)}"
        print(f"Results saved to {csv_url}")
        return csv_url
    except Exception as e:
        print(f"Failed to upload results CSV: {e}")
        return None

async def process_csv(csv_data, req_id):
    reader = csv.DictReader(csv_data.splitlines())
    results = []
    error_occurred = False

    for row in reader:
        serial_number = row.get('S. No.')
        product_name = row.get('Product Name')
        input_urls_string = row.get('Input Image Urls')
        input_urls = [url.strip('"').strip() for url in input_urls_string.split(',')]

        tasks = [process_image(url, req_id, product_name) for url in input_urls]

        try:
            output_urls = await asyncio.gather(*tasks)
            output_urls = [url for url in output_urls if url is not None]

            if len(output_urls) != len(input_urls):
                error_occurred = True

            results.append({
                "S. No.": serial_number,
                "Product Name": product_name,
                "Input Image Urls": input_urls,
                "Output Image Urls": output_urls
            })
        except Exception as err:
            error_occurred = True
            print(f"Error processing row {row}: {err}")
            results.append({
                "S. No.": serial_number,
                "Product Name": product_name,
                "Input Image Urls": input_urls,
                "Output Image Urls": []
            })

    try:
        csv_url = await save_results_to_csv(results, req_id)
    except Exception as e:
        error_occurred = True
        print(f"Failed to save results to CSV: {e}")
        csv_url = None

    status = "Completed" if csv_url and not error_occurred else "Failed"
    if error_occurred:
        status = "Completed with Errors" if csv_url else "Failed"

    update_item = {
        "status": status,
        "output_url": csv_url if csv_url else ""
    }

    try:
        await db_ops.update_job_status(req_id, update_item)
        await db_ops.insert_product({req_id: results})
    except Exception as e:
        print(f"Failed to update job status or insert product data: {e}")
        await db_ops.update_job_status(req_id, {"status": "Failed", "error": str(e)})
