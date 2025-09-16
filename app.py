import os
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
# from chainlit.data.dynamodb import DynamoDBDataLayer
from chainlit.data.storage_clients.s3 import S3StorageClient
from typing import Any, Dict, Union
from chainlit.logger import logger


class SupabaseS3StorageClient(S3StorageClient):
    """Custom S3StorageClient that generates correct Supabase public URLs"""
    
    def __init__(self, bucket: str, supabase_url: str, **kwargs: Any):
        super().__init__(bucket, **kwargs)
        self.supabase_url = supabase_url.rstrip('/')
        logger.info("SupabaseS3StorageClient initialized")
    
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
            # Generate correct Supabase public URL
            url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{object_key}"
            logger.info(f"SupabaseS3StorageClient generated URL: {url}")
            return {"object_key": object_key, "url": url}
        except Exception as e:
            logger.warning(f"SupabaseS3StorageClient, upload_file error: {e}")
            return {}
    
    def sync_get_read_url(self, object_key: str) -> str:
        """Generate correct Supabase public URL for reading"""
        try:
            url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{object_key}"
            logger.info(f"SupabaseS3StorageClient get_read_url: {url}")
            return url
        except Exception as e:
            logger.warning(f"SupabaseS3StorageClient, get_read_url error: {e}")
            return object_key
    
    async def get_read_url(self, object_key: str) -> str:
        """Async version of get_read_url"""
        return self.sync_get_read_url(object_key)


db_conn = os.getenv("DATABASE_URL", "")
bucket = os.getenv("BUCKET_NAME", "")
aws_access_key = os.getenv("APP_AWS_ACCESS_KEY", "")
aws_secret_key = os.getenv("APP_AWS_SECRET_KEY", "")
aws_region = os.getenv("APP_AWS_REGION", "")
aws_endpoint = os.getenv("DEV_AWS_ENDPOINT", "")
supabase_url = os.getenv("SUPABASE_URL", "")

storage_client = SupabaseS3StorageClient(
    bucket=bucket,
    supabase_url=supabase_url,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region,
    endpoint_url=aws_endpoint
)


@cl.data_layer
def get_data_layer():
    # DynamoDBDataLayer(table_name="<Your Table>", storage_provider=storage_client)
    return SQLAlchemyDataLayer(conninfo=db_conn, storage_provider=storage_client)


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_chat_resume
async def on_chat_resume(thread):
    pass


@cl.step(type="tool")
async def tool():
    # Fake tool
    await cl.sleep(2)
    return "Response from the tool!"


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """

    # Call the tool
    tool_res = await tool()

    await cl.Message(content=tool_res).send()
