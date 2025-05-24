import os
import logging
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.config import Config as BotoConfig
from Config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
class S3Uploader:
    def __init__(self):
        """
        Initializes the S3 uploader using provided parameters or falls back to configuration.
        """
        Config.load()
        self.access_key = Config.get('duck_access_key')
        self.secret_key = Config.get('duck_secret_access_key')
        self.bucket_name = Config.get('duck_bucket_name')
        raw_storage_url = Config.get("duck_storage_url")
        
        # Добавление схемы, если отсутствует
        if not raw_storage_url.startswith("http://") and not raw_storage_url.startswith("https://"):
            self.storage_url = "https://" + raw_storage_url
        else:
            self.storage_url = raw_storage_url
        
        # Настройка boto3 клиента с отключением подписания полезной нагрузки
        boto_config = BotoConfig(s3={"payload_signing_enabled": False})
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.storage_url,  # Использование кастомного storage URL
            config=boto_config
        )

    def upload_file(self, local_file, remote_file):
        """
        Uploads a local file to the specified S3 bucket.
        Automatically deletes the remote file if it exists (thus simulating overwrite).
        """
        if not os.path.exists(local_file):
            logger.error(f"Local file {local_file} does not exist.")
            return None

        try:
            # Check if the file already exists and delete it
            self.s3_client.head_object(Bucket=self.bucket_name, Key=remote_file)
            logger.info(f"File {remote_file} exists. Deleting it.")
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_file)
        except self.s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                logger.error(f"Error checking for existing file: {e}")
                return None

        # Now, upload the file
        try:
            self.s3_client.upload_file(local_file, self.bucket_name, remote_file)
            logger.info(f"File uploaded successfully to s3://{self.bucket_name}/{remote_file}")
            return f"s3://{self.bucket_name}/{remote_file}"
        except NoCredentialsError:
            logger.error("Credentials not available.")
            return None
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None

    def generate_public_link(self, remote_file):
        """
        Generates a public URL for a file assuming a public S3 bucket.
        """
        public_url = f"https://{self.bucket_name}.s3.amazonaws.com/{remote_file}"
        logger.info(f"Public URL: {public_url}")
        return public_url

# Example usage:
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LOCAL_FILE = "video/output.mp4"
    REMOTE_FILE = "output.mp4"
    
    uploader = S3Uploader()
    remote_path = uploader.upload_file(LOCAL_FILE, REMOTE_FILE)
    if remote_path:
        public_link = uploader.generate_public_link(REMOTE_FILE)
        print(f"Public link: {public_link}")