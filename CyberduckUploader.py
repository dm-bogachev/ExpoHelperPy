import os
import subprocess
import logging
from Config import Config

logger = logging.getLogger(__name__)

class CyberduckUploader:
    def __init__(self, remote_url=None, profile=None, access_key=None, secret_key=None,
                 bucket_name=None, storage_url=None):
        """
        Initializes the uploader using provided parameters or falls back to configuration.
        The Config is loaded automatically.
        """
        Config.load()
        self.profile = profile or f"./data/{Config.get('duck_profile')}"
        self.access_key = access_key or Config.get('duck_access_key')
        self.secret_key = secret_key or Config.get('duck_secret_access_key')
        self.bucket_name = bucket_name or Config.get('duck_bucket_name')
        self.storage_url = storage_url or Config.get('duck_storage_url')

        # Build the remote URL if not explicitly passed.
        if remote_url:
            self.remote_url = remote_url.rstrip('/')
        else:
            self.remote_url = f"s3://{self.storage_url}/{self.bucket_name}"

    def upload_file(self, local_file, remote_file):
        """
        Uploads a local file to the remote destination using Cyberduck.
        Automatically deletes the remote file if it exists (thus simulating overwrite).
        """
        if not os.path.exists(local_file):
            logger.error(f"Local file {local_file} does not exist.")
            return None

        full_remote = f"{self.remote_url}/{remote_file}"
        base_command = ["duck"]
        if self.profile:
            base_command += ["--profile", self.profile]
        if self.access_key and self.secret_key:
            base_command += ["--username", self.access_key, "--password", self.secret_key]

        # First, delete the remote file if it exists
        delete_command = base_command + ["--delete", full_remote]
        logger.info(f"Attempting to delete remote file (if exists): {' '.join(delete_command)}")
        subprocess.run(delete_command, text=True, capture_output=True)
        # Если удаление не удалось, это не критично – продолжаем загрузку.

        # Now, upload the file
        upload_command = base_command + ["--upload", full_remote, local_file]
        logger.info(f"Running command: {' '.join(upload_command)}")
        result = subprocess.run(upload_command, text=True, capture_output=True)
        if result.returncode != 0:
            logger.error(f"Error uploading file: {result.stderr}")
            return None

        logger.info(f"File uploaded successfully to {full_remote}")
        return full_remote

    def generate_public_link(self, remote_file):
        """
        Generates a public URL for a file assuming a public S3 bucket.
        """
        public_url = f"https://{self.bucket_name}.{self.storage_url}/{remote_file}"
        logger.info(f"Public URL: {public_url}")
        return public_url

# Пример использования:
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    LOCAL_FILE = "video/output.mp4"
    REMOTE_FILE = "output.mp4"
    
    uploader = CyberduckUploader()
    remote_path = uploader.upload_file(LOCAL_FILE, REMOTE_FILE)
    if remote_path:
        public_link = uploader.generate_public_link(REMOTE_FILE)
        print(f"Public link: {public_link}")