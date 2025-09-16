import os
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
# from chainlit.data.dynamodb import DynamoDBDataLayer
from chainlit.data.storage_clients.s3 import S3StorageClient


db_conn = os.getenv("DATABASE_URL", "")
bucket = os.getenv("BUCKET_NAME", "")
aws_access_key = os.getenv("APP_AWS_ACCESS_KEY", "")
aws_secret_key = os.getenv("APP_AWS_SECRET_KEY", "")
aws_region = os.getenv("APP_AWS_REGION", "")
aws_endpoint = os.getenv("DEV_AWS_ENDPOINT", "")

storage_client = S3StorageClient(
    bucket=bucket,
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
