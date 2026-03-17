import os
import uuid
import abc
import boto3
from PIL import Image
from typing import Protocol, runtime_checkable
from app.core.config import settings
from botocore.exceptions import ClientError
import shutil

THUMB_SIZE = (300, 300)

@runtime_checkable
class StorageService(Protocol):
    @abc.abstractmethod
    async def save(self, file) -> str:
        """Saves the file and returns its path/identifier."""
        pass

    @abc.abstractmethod
    def get_url(self, file_path: str) -> str:
        """Returns a URL where the file can be accessed."""
        pass

    @abc.abstractmethod
    async def get_local_path(self, file_path: str) -> str:
        """Returns a local path to the file. Downloads it if necessary."""
        pass

    @abc.abstractmethod
    async def cleanup_local(self, temp_path: str):
        """Cleans up temporary files if any."""
        pass

class LocalStorageService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.thumb_dir = os.path.join(upload_dir, "thumbs")
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.thumb_dir, exist_ok=True)

    async def save(self, file) -> str:
        ext = file.filename.split(".")[-1]
        name = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(self.upload_dir, name)

        with open(path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        try:
            with Image.open(path) as img:
                img.thumbnail(THUMB_SIZE)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                thumb_path = os.path.join(self.thumb_dir, name)
                img.save(thumb_path)
        except Exception as e:
            print(f"Błąd generowania miniatury: {e}")

        # Return relative path for database compatibility
        return os.path.join(self.upload_dir, name).replace("\\", "/")

    def get_url(self, file_path: str) -> str:
        if not file_path.startswith("/"):
            return f"/{file_path}"
        return file_path

    async def get_local_path(self, file_path: str) -> str:
        # For local storage, it's already local
        return file_path

    async def cleanup_local(self, temp_path: str):
        # No cleanup needed for local files as they are permanent
        pass

class S3StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL
        )
        self.bucket = settings.S3_BUCKET
        self.temp_dir = "temp_processing"
        os.makedirs(self.temp_dir, exist_ok=True)

    async def save(self, file) -> str:
        ext = file.filename.split(".")[-1]
        name = f"{uuid.uuid4()}.{ext}"
        content = await file.read()
        
        # Upload original
        self.s3.put_object(Bucket=self.bucket, Key=name, Body=content)
        
        # Generate and upload thumbnail
        try:
            import io
            with Image.open(io.BytesIO(content)) as img:
                img.thumbnail(THUMB_SIZE)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                thumb_io = io.BytesIO()
                img.save(thumb_io, format="JPEG")
                thumb_io.seek(0)
                
                thumb_name = f"thumbs/{name}"
                self.s3.put_object(Bucket=self.bucket, Key=thumb_name, Body=thumb_io)
        except Exception as e:
            print(f"Błąd generowania miniatury S3: {e}")

        return name

    def get_url(self, file_path: str) -> str:
        # In this implementation, we assume we want public URLs or signed URLs.
        # For now, let's return a simple URL if it's minio/local,
        # or we could generate a presigned URL.
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': file_path},
                ExpiresIn=3600
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return file_path

    async def get_local_path(self, file_path: str) -> str:
        local_path = os.path.join(self.temp_dir, os.path.basename(file_path))
        self.s3.download_file(self.bucket, file_path, local_path)
        return local_path

    async def cleanup_local(self, temp_path: str):
        if os.path.exists(temp_path) and self.temp_dir in temp_path:
            os.remove(temp_path)

def get_storage() -> StorageService:
    if settings.STORAGE == "cloud":
        return S3StorageService()
    return LocalStorageService()
