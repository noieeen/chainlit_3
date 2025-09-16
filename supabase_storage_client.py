import os
from typing import Any, Dict, Union

import boto3  # type: ignore

from chainlit import make_async
from chainlit.data.storage_clients.base import BaseStorageClient, storage_expiry_time
from chainlit.logger import logger


class SupabaseStorageClient(BaseStorageClient):
    """
    Custom storage client for Supabase S3-compatible storage that generates
    correct public URLs for Supabase storage buckets.
    """

    def __init__(self, bucket: str, supabase_url: str, **kwargs: Any):
        try:
            self.bucket = bucket
            self.supabase_url = supabase_url.rstrip('/')  # Remove trailing slash
            self.client = boto3.client("s3", **kwargs)
            logger.info("SupabaseStorageClient initialized")
        except Exception as e:
            logger.warning(f"SupabaseStorageClient initialization error: {e}")

    def sync_get_read_url(self, object_key: str) -> str:
        """
        Generate a public URL for Supabase storage.
        Supabase public URLs follow the pattern:
        https://[project-id].supabase.co/storage/v1/object/public/[bucket]/[object_key]
        """
        try:
            # For Supabase, we generate public URLs directly
            public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{object_key}"
            return public_url
        except Exception as e:
            logger.warning(f"SupabaseStorageClient, get_read_url error: {e}")
            return object_key

    async def get_read_url(self, object_key: str) -> str:
        return await make_async(self.sync_get_read_url)(object_key)

    def sync_upload_file(
        self,
        object_key: str,
        data: Union[bytes, str],
        mime: str = "application/octet-stream",
        overwrite: bool = True,
        content_disposition: str | None = None,
    ) -> Dict[str, Any]:
        try:
            if content_disposition is not None:
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=object_key,
                    Body=data,
                    ContentType=mime,
                    ContentDisposition=content_disposition,
                )
            else:
                self.client.put_object(
                    Bucket=self.bucket, Key=object_key, Body=data, ContentType=mime
                )
            
            # Generate the correct Supabase public URL
            public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{object_key}"
            logger.info(f"SupabaseStorageClient generated URL: {public_url}")
            return {"object_key": object_key, "url": public_url}
        except Exception as e:
            logger.warning(f"SupabaseStorageClient, upload_file error: {e}")
            return {}

    async def upload_file(
        self,
        object_key: str,
        data: Union[bytes, str],
        mime: str = "application/octet-stream",
        overwrite: bool = True,
        content_disposition: str | None = None,
    ) -> Dict[str, Any]:
        return await make_async(self.sync_upload_file)(
            object_key, data, mime, overwrite, content_disposition
        )

    def sync_delete_file(self, object_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except Exception as e:
            logger.warning(f"SupabaseStorageClient, delete_file error: {e}")
            return False

    async def delete_file(self, object_key: str) -> bool:
        return await make_async(self.sync_delete_file)(object_key)
