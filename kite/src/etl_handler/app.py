"""
Lambda function to process Kinesis stream data and upsert into Aurora database.

This module handles the ETL process for order data, reading from a Kinesis stream
and upserting the data into an Aurora PostgreSQL database using a connection pool
for improved performance.
"""

import json
import os
import base64
import logging
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError
from psycopg2.pool import SimpleConnectionPool

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global variables
connection_pool = None
secrets_manager_client = None
db_credentials = None

# Environment variables
AURORA_SECRET = os.environ['AURORA_SECRET_NAME']

def get_secret(secret_name: str) -> Dict[str, Any]:
    """
    Retrieve a secret from AWS Secrets Manager.

    This function caches the retrieved secret to minimize API calls.

    Args:
        secret_name (str): The name of the secret to retrieve.

    Returns:
        Dict[str, Any]: The secret key/value pairs.

    Raises:
        ClientError: If there's an error retrieving the secret.
    """
    global secrets_manager_client, db_credentials
    if db_credentials is None:
        if not secrets_manager_client:
            secrets_manager_client = boto3.client('secretsmanager')
        try:
            response = secrets_manager_client.get_secret_value(SecretId=secret_name)
            db_credentials = json.loads(response['SecretString'])
        except ClientError as e:
            logger.error(f"Error retrieving secret: {str(e)}")
            raise
    return db_credentials

def get_connection_pool():
    """
    Create or return an existing database connection pool.

    This function ensures that only one connection pool is created and reused
    across multiple invocations of the Lambda function.

    Returns:
        SimpleConnectionPool: A connection pool for the Aurora database.

    Raises :
        Exception: If there's an error creating the connection pool.
    """
    global connection_pool
    if connection_pool is None:
        try:
            aurora_secret = get_secret(AURORA_SECRET)
            connection_pool = SimpleConnectionPool(
                1, 5,  # min_connections, max_connections
                host=aurora_secret['host'],
                port=aurora_secret['port'],
                dbname=aurora_secret['dbname'],
                user=aurora_secret['username'],
                password=aurora_secret['password'],
                sslmode='require'
            )
            logger.info("Successfully created connection pool")
        except Exception as e:
            logger.error(f"Error creating connection pool: {str(e)}")
            raise
    return connection_pool

def upsert_order(cursor, data: Dict[str, Any]):
    """
    Upsert an order into the database.

    This function performs an INSERT ... ON CONFLICT DO UPDATE operation
    to either insert a new order or update an existing one.

    Args:
        cursor: A database cursor.
        data (Dict[str, Any]): The order data to upsert.

    Raises:
        psycopg2.Error: If there's a database error during the upsert operation.
    """
    cursor.execute(
        """
        INSERT INTO orders (
            order_number, kpid, coi, material_type, product, 
            country, run_type, process_type, mfg_organization
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_number) DO UPDATE SET
            kpid = EXCLUDED.kpid,
            coi = EXCLUDED.coi,
            material_type = EXCLUDED.material_type,
            product = EXCLUDED.product,
            country = EXCLUDED.country,
            run_type = EXCLUDED.run_type,
            process_type = EXCLUDED.process_type,
            mfg_organization = EXCLUDED.mfg_organization
        """,
        (
            int(data['order_number']), data['kpid'], data['coi'], 
            data['material_type'], data['product'], data['country'], 
            data['run_type'], data['process_type'], data['mfg_organization']
        )
    )

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function to process Kinesis stream records and upsert into Aurora.

    This function reads records from the Kinesis stream, decodes the data,
    and upserts it into the Aurora database.

    Args:
        event (Dict[str, Any]): The event data from the Kinesis stream.
        context (Any): The Lambda context object.

    Returns:
        Dict[str, Any]: A response object indicating success or failure.
    """
    try:
        pool = get_connection_pool()
        with pool.getconn() as conn:
            with conn.cursor() as cursor:
                for record in event['Records']:
                    payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
                    event_data = json.loads(payload)
                    logger.info(f"Received data: {event_data}")
                    
                    # Extract the 'data' field from the event_data
                    data = event_data.get('data')
                    
                    if data:
                        try:
                            upsert_order(cursor, data)
                            conn.commit()
                            logger.info(f"Successfully upserted order: {data['order_number']}")
                        except KeyError as ke:
                            logger.error(f"Missing key in data: {str(ke)}")
                            conn.rollback()
                        except ValueError as ve:
                            logger.error(f"Invalid value for order_number: {data.get('order_number', 'N/A')}")
                            conn.rollback()
                    else:
                        logger.warning("Received event without 'data' field")

        pool.putconn(conn)

        return {
            'statusCode': 200,
            'body': json.dumps('Data upserted to Aurora successfully')
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

# Initialize the connection pool during module import
get_connection_pool()

# This part runs once per Lambda "cold start"
logger.info("Lambda initialization completed")
