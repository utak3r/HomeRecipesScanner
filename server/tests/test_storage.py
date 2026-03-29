import os
import pytest
import shutil
from unittest.mock import MagicMock
from app.services.storage import LocalStorageService, S3StorageService
from app.core.config import settings
from moto import mock_aws
import boto3

@pytest.fixture
def local_storage():
    test_dir = "test_uploads"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    service = LocalStorageService(upload_dir=test_dir)
    yield service
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

@pytest.mark.asyncio
async def test_local_storage_save(local_storage):
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    
    # Create a real small image for testing
    from PIL import Image
    import io
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_data = img_byte_arr.getvalue()
    
    # Async mock for file.read()
    async def async_read():
        return img_data
    mock_file.read = async_read
    
    path = await local_storage.save(mock_file)
    
    assert os.path.exists(path)
    assert path.startswith("test_uploads/")
    
    thumb_path = path.replace("test_uploads/", "test_uploads/thumbs/")
    assert os.path.exists(thumb_path)
    
def test_local_storage_get_url_with_base_url():
    from app.core.config import settings
    original_base_url = settings.BASE_URL
    original_storage = settings.STORAGE
    
    try:
        settings.BASE_URL = "http://localhost:8000"
        settings.STORAGE = "local"
        service = LocalStorageService()
        
        url = service.get_url("uploads/test.jpg")
        assert url == "http://localhost:8000/uploads/test.jpg"
        
        url = service.get_url("/uploads/test.jpg")
        assert url == "http://localhost:8000/uploads/test.jpg"
        
        # Test with trailing slash in BASE_URL
        settings.BASE_URL = "http://localhost:8000/"
        url = service.get_url("uploads/test.jpg")
        assert url == "http://localhost:8000/uploads/test.jpg"
        
    finally:
        settings.BASE_URL = original_base_url
        settings.STORAGE = original_storage

@mock_aws
def test_s3_storage_save_sync():
    # Setup mock S3
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket="test-bucket")
    
    # Update settings for test
    from app.core.config import settings
    settings.S3_BUCKET = "test-bucket"
    settings.STORAGE = "cloud"
    settings.S3_ENDPOINT_URL = None # Use default for moto
    
    service = S3StorageService()
    
    mock_file = MagicMock()
    mock_file.filename = "cloud_test.png"
    
    from PIL import Image
    import io
    img = Image.new('RGB', (100, 100), color = 'blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_data = img_byte_arr.getvalue()
    
    # Workaround for async save in sync test
    import asyncio
    
    async def run_test():
        async def async_read():
            return img_data
        mock_file.read = async_read
        return await service.save(mock_file)
    
    key = asyncio.run(run_test())
    
    # Check if file exists in S3
    s3 = boto3.client("s3", region_name="us-east-1")
    objects = s3.list_objects(Bucket="test-bucket")['Contents']
    keys = [obj['Key'] for obj in objects]
    
    assert key in keys
    assert f"thumbs/{key}" in keys

@mock_aws
def test_s3_storage_get_local_path_sync():
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket="test-bucket")
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.put_object(Bucket="test-bucket", Key="test_file.txt", Body=b"hello s3")
    
    service = S3StorageService()
    
    import asyncio
    local_p = asyncio.run(service.get_local_path("test_file.txt"))
    
    assert os.path.exists(local_p)
    with open(local_p, "rb") as f:
        assert f.read() == b"hello s3"
        
    asyncio.run(service.cleanup_local(local_p))
    assert not os.path.exists(local_p)
