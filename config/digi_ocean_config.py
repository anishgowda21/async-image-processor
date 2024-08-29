import aioboto3
import os

ACCESS_ID = os.getenv("ACCESS_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
REGION_NAME = 'blr1'  # DigitalOcean region name should be in lowercase
ENDPOINT_URL = 'https://imagecompress211.blr1.digitaloceanspaces.com'


async def upload(file_obj, bucket_name, obj_name):
    session = aioboto3.Session(
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION_NAME
    )

    async with session.client("s3", endpoint_url=ENDPOINT_URL) as s3:
        try:
            print(f"Uploading {obj_name} to DigitalOcean Spaces")
            await s3.upload_fileobj(file_obj, bucket_name, obj_name,ExtraArgs={"ACL": "public-read"})
            print(f"Finished Uploading {obj_name} to DigitalOcean Spaces")
        except Exception as e:
            print(f"Unable to upload {obj_name} to {bucket_name}: {e} ({type(e)})")
            return ""
