# services/aph_delivery_and_release_service.py

from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas.aph_delivery_and_release_batch_schema import APHDeliveryReleaseBatchSchema

async def retrieve_all_async(session: Session):
    """
    Asynchronously retrieves all APH Delivery and Release records from the database.

    This function works with both synchronous and asynchronous database sessions.

    Args:
        session (Session): The database session, which can be either synchronous or asynchronous.

    Returns:
        list: A list of APHDeliveryReleaseBatchSchema objects representing all records.
    """
    # Create a SELECT statement for all records
    statement = select(APHDeliveryReleaseBatchSchema)

    # Execute the statement based on the session type
    if isinstance(session, Session):
        # For synchronous sessions
        result = await session.execute(statement)
    else:
        # For asynchronous sessions
        result = session.execute(statement)

    # Retrieve all results as a list of APHDeliveryReleaseBatchSchema objects
    aph_deliveries = result.scalars().all()
    return aph_deliveries

async def retrieve_by_id_async(session: Session | Session, order_number: int):
    """
    Retrieves an Order by its ID from the database.

    Args:
        session (Session): The session for database operations.
        order_number (int): The ID of the Order to retrieve.

    Returns:
        The Order matching the provided ID, or None if not found.
    """
    order_number = int(order_number)
    aph_delivery = session.get(APHDeliveryReleaseBatchSchema, order_number)
    return aph_delivery




