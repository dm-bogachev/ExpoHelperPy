import boto3
from botocore.exceptions import ClientError
import os
from Config import Config as ConfigF
from botocore.config import Config
import logging

logger = logging.getLogger("s3loader")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, ConfigF.get("debug_level", "INFO"))
)

# Конфигурация из переменных окружения
ACCESS_KEY = ConfigF.get("access_key")
SECRET_KEY = ConfigF.get("secret_key")
ENDPOINT_URL = ConfigF.get("endpoint_url")
BUCKET_NAME = ConfigF.get("bucket_name")

config = Config(
    s3={'addressing_style': 'path'},
    signature_version='s3'
)

def upload_file(source_file, destination_file):

    logger.info(f"Uploading file from {source_file} to {destination_file} in bucket {BUCKET_NAME}")
    retval = True

    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=ENDPOINT_URL,
        config=config
    )
    try:
        s3.upload_file(source_file, 
                       BUCKET_NAME, 
                       destination_file, 
                       ExtraArgs={"ContentType": "video/mp4",
                                   "ContentDisposition": "inline"})
        logger.info("File uploaded successfully. Checking if the file actually exists in the bucket...")

        try:
            s3.head_object(Bucket=BUCKET_NAME, Key=destination_file)
            logger.info(f"File '{destination_file}' successfully uploaded and exists in the bucket.")
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                logger.warning(f"File '{destination_file}' not found.")
                retval = False
            else:
                logger.error(f"Error occurred: {e}")
    except ClientError as e:
        logger.error(f"Error occurred: {e}")
    finally:
        if hasattr(s3, "close"):
            s3.close()
    return retval

def get_file_url(file_name):
    return f"{ENDPOINT_URL}/{BUCKET_NAME}/{file_name}"

if __name__ == "__main__":
    upload_file("./shared_data/expo_helper.db", "test.txt")
    upload_file("./shared_data/expo_helper.db", "test2.txt")

