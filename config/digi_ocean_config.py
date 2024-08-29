import aioboto3
from dotenv import load_dotenv
import os

load_dotenv()

class DigiOceanClient:
    def __init__(self, access_id, secret_key, region_name, endpoint_url):
        self.access_id = access_id
        self.secret_key = secret_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.session = None

    async def __aenter__(self):
        self.session = aioboto3.Session()
        self.client = await self.session.client(
            's3',
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_id,
            aws_secret_access_key=self.secret_key
        ).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.__aexit__(exc_type, exc, tb)
        await self.session.__aexit__(exc_type, exc, tb)

    async def upload_fileobj(self, file_obj, bucket_name, object_name):
        try:
            async with self.client as client:
                await client.upload_fileobj(file_obj, bucket_name, object_name)
                print(f"File uploaded to {bucket_name}/{object_name} successfully.")
        except Exception as e:
            print(f"Failed to upload file to {bucket_name}/{object_name}: {e}")

# Environment variables
ACCESS_ID = os.getenv("ACCESS_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
REGION_NAME = 'BLR1'
ENDPOINT_URL = 'https://imagecompress211.blr1.digitaloceanspaces.com'

# Instantiate the client
do_client = DigiOceanClient(ACCESS_ID, SECRET_KEY, REGION_NAME, ENDPOINT_URL)
