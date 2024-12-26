# ------------------------------------------------------------------------------
# Service
# ------------------------------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.aph_delivery_and_release_live_schema import APHDeliveryReleaseLiveSchema
from sqlalchemy.orm import Session

# Retrieve ---------------------------------------------------------------------

async def retrieve_all_async(session: AsyncSession | Session):
    """
    Retrieves all the orders from the database.

    Args:
        session (AsyncSession | Session): The session for database operations.

    Returns:
        A collection with all the orders.
    """
    statement = select(APHDeliveryReleaseLiveSchema)
    
    if isinstance(session, AsyncSession):
        # Aurora (async)
        result = await session.execute(statement)
        orders = result.scalars().all()
    else:
        # Redshift (sync)
        result = session.execute(statement)
        orders = result.scalars().all()
    
    return orders

async def retrieve_by_id_async(session: AsyncSession | Session, order_number: int):
    """
    Retrieves an Order by its ID from the database.

    Args:
        session (AsyncSession | Session): The session for database operations.
        order_number (int): The ID of the Order to retrieve.

    Returns:
        The Order matching the provided ID, or None if not found.
    """
    order_number = int(order_number)
    
    if isinstance(session, AsyncSession):
        order = await session.get(APHDeliveryReleaseLiveSchema, order_number)
    else:
        order = session.get(APHDeliveryReleaseLiveSchema, order_number)
    
    return order



