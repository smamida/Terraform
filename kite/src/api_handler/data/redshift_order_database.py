import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from typing import Generator
import json
import os

# Configure logging
logger = logging.getLogger("uvicorn")

# Read configuration from environment variables
REDSHIFT_SECRET = os.environ.get('REDSHIFT_SECRET')
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

def create_redshift_url(secret_dict: dict) -> str:
    return (f"redshift+psycopg2://{secret_dict['username']}:{secret_dict['password']}@"
            f"{secret_dict['host']}:{secret_dict.get('port', '5439')}/{secret_dict['dbname']}")

# Reading secret from secret manager
secret_dict = get_secret(REDSHIFT_SECRET, REGION_NAME)
REDSHIFT_URL = create_redshift_url(secret_dict)

# Create engine and sessionmaker for Redshift
redshift_engine = create_engine(REDSHIFT_URL, echo=True)
RedshiftSessionMaker = sessionmaker(bind=redshift_engine, autocommit=False, autoflush=False)

RedshiftBase = declarative_base()

def generate_redshift_session() -> Generator[sessionmaker, None, None]:
    """
    Dependency function to yield a Redshift ORM session.

    Yields:
        Session: An instance of a SQLAlchemy ORM session for Redshift.
    """
    session = RedshiftSessionMaker()
    try:
        yield session
    finally:
        session.close()
