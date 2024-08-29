from boto3 import session
from dotenv import load_dotenv
import os

load_dotenv()

class DigiOceanClient:
    def __init__(self, access_id, secret_key, region_name, endpoint_url):
        # Initiate session
        self.session = session.Session()
        self.client = self.session.client(
            's3',
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=access_id,
            aws_secret_access_key=secret_key
        )

    def upload_file(self, file_name, bucket_name, object_name):
        """Upload a file to the specified bucket."""
        try:
            self.client.upload_file(file_name, bucket_name, object_name)
            print(f"File {file_name} uploaded to {bucket_name}/{object_name} successfully.")
        except Exception as e:
            print(f"Failed to upload {file_name} to {bucket_name}/{object_name}: {e}")


ACCESS_ID = os.getenv("ACCESS_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
REGION_NAME = 'BLR1'
ENDPOINT_URL = 'https://imagecompress211.blr1.digitaloceanspaces.com'


do_client = DigiOceanClient(ACCESS_ID, SECRET_KEY, REGION_NAME, ENDPOINT_URL)
