import boto3
from botocore.exceptions import ClientError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from typing import AsyncGenerator
import json
import os

# Configure logging
logger = logging.getLogger("uvicorn")
logging.getLogger("sqlalchemy.engine.Engine").handlers = logger.handlers

# Read configuration from environment variables
SECRET_NAME = os.environ.get('AURORA_SECRET')
REGION_NAME = os.environ.get('REGION_NAME')

def get_secret(secret_name: str, region_name: str) -> dict:
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get('SecretString') or response.get('SecretBinary')
        return json.loads(secret_string)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_map = {
            'ResourceNotFoundException': f"The requested secret {secret_name} was not found",
            'InvalidRequestException': f"The request was invalid due to: {e}",
            'InvalidParameterException': f"The request had invalid params: {e}",
            'DecryptionFailure': f"The requested secret can't be decrypted using the provided KMS key: {e}",
            'InternalServiceError': f"An error occurred on service side: {e}"
        }
        logger.error(error_map.get(error_code, f"An unexpected error occurred: {e}"))
        raise

def create_database_url(secret_dict: dict) -> str:
    return (f"postgresql+asyncpg://{secret_dict['username']}:{secret_dict['password']}@"
            f"{secret_dict['host']}:{secret_dict.get('port', '5432')}/{secret_dict['dbname']}")

# reading secret from secret manager
secret_dict = get_secret(SECRET_NAME, REGION_NAME)
DATABASE_URL = create_database_url(secret_dict)

# Create async engine and sessionmaker
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_sessionmaker = sessionmaker(bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False)

Base = declarative_base()

async def generate_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to yield an async PgSQL ORM session.

    Yields:
        AsyncSession: An instance of an async SQLAlchemy ORM session.
    """
    async with async_sessionmaker() as async_session:
        yield async_session
