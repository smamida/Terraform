# ------------------------------------------------------------------------------
# Route
# ------------------------------------------------------------------------------

from typing import List, Dict,Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from data.aurora_order_database import generate_async_session
from data.redshift_order_database import generate_redshift_session
from models.aph_delivery_and_release_live_model import OrderModel
from services import aph_delivery_and_release_live_service


api_router = APIRouter()

CACHING_TIME_IN_SECONDS = 600

# POST -------------------------------------------------------------------------

@api_router.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    summary="Creates a new Order",
    tags=["Orders"]
)
async def post_async(
    order_model: OrderModel = Body(...),
    async_session: AsyncSession = Depends(generate_async_session)
):
    """
    Endpoint to create a new order.

    Args:
        order_model (OrderModel): The Pydantic model representing the Order to create.
        async_session (AsyncSession): The async version of a SQLAlchemy ORM session.

    Raises:
        HTTPException: HTTP 409 Conflict error if the order already exists.
    """
    order = await aph_delivery_and_release_live_service.retrieve_by_id_async(async_session, order_model.order_number)
    if order:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order already exists")
    await aph_delivery_and_release_live_service.create_async(async_session, order_model)
    await FastAPICache.clear()
    return {"message": f"Order {order_model.order_number} created successfully"}

# GET --------------------------------------------------------------------------


@api_router.get(
    "/orders",
    response_model=Dict[str, List[OrderModel]],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a collection of Orders",
    tags=["Orders"]
)
@cache(expire=CACHING_TIME_IN_SECONDS)
async def get_all_async(
    live: bool = Query(False, description="Query live data from Aurora"),
    batch: bool = Query(False, description="Query batch data from Redshift"),
    aurora_session: AsyncSession = Depends(generate_async_session),
    redshift_session: AsyncSession = Depends(generate_redshift_session)
):
    """
    Endpoint to retrieve all orders from specified data sources.

    Args:
        live (bool): Flag to query live data from Aurora.
        batch (bool): Flag to query batch data from Redshift.
        aurora_session (AsyncSession): The async version of an Aurora ORM session.
        redshift_session (AsyncSession): The async version of a Redshift ORM session.

    Returns:
        Dict[str, List[OrderModel]]: A dictionary containing real-time and batch data.

    Raises:
        HTTPException: If neither live nor batch flag is set to True.
    """
    if not live and not batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'live' or 'batch' must be set to true"
        )

    response = {}

    if live:
        live_orders = await aph_delivery_and_release_live_service.retrieve_all_async(aurora_session)
        response["real_time_data"] = live_orders

    if batch:
        batch_orders = await aph_delivery_and_release_live_service.retrieve_all_async(redshift_session)
        response["batch_data"] = batch_orders

    return response



@api_router.get(
    "/orders/{order_number}",
    response_model=Dict[str, Optional[OrderModel]],
    status_code=status.HTTP_200_OK,
    summary="Retrieves an Order by its Id",
    tags=["Orders"]
)
@cache(expire=CACHING_TIME_IN_SECONDS)
async def get_by_id_async(
    order_number: int = Path(..., title="The Id of the order"),
    live: bool = Query(False, description="Query live data from Aurora"),
    batch: bool = Query(False, description="Query batch data from Redshift"),
    aurora_session: AsyncSession = Depends(generate_async_session),
    redshift_session: AsyncSession = Depends(generate_redshift_session)
):
    """
    Endpoint to retrieve an order by its ID from specified data source(s).

    Args:
        order_number (int): The ID of the order to retrieve.
        live (bool): Flag to query live data from Aurora.
        batch (bool): Flag to query batch data from Redshift.
        aurora_session (AsyncSession): The async version of an Aurora ORM session.
        redshift_session (AsyncSession): The async version of a Redshift ORM session.

    Returns:
        Dict[str, Optional[OrderModel]]: A dictionary containing real-time and/or batch data.

    Raises:
        HTTPException: 
            - 400 Bad Request if neither live nor batch flag is set to True.
            - 404 Not Found if the order with the specified ID does not exist in any queried data source.
    """
    if not live and not batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'live' or 'batch' must be set to true"
        )

    response = {}

    if live:
        live_order = await aph_delivery_and_release_live_service.retrieve_by_id_async(aurora_session, order_number)
        if live_order:
            response["real_time_data"] = OrderModel.from_orm(live_order)

    if batch:
        batch_order = await aph_delivery_and_release_live_service.retrieve_by_id_async(redshift_session, order_number)
        if batch_order:
            response["batch_data"] = OrderModel.from_orm(batch_order)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_number} not found in the specified data source(s)"
        )

    return response

# PUT --------------------------------------------------------------------------


@api_router.put(
    "/orders/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Updates an existing Order",
    tags=["Orders"]
)
async def put_async(
    order_number: int = Path(..., title="The ID of the order"),
    order_model: OrderModel = Body(...),
    async_session: AsyncSession = Depends(generate_async_session)
):
    """
    Endpoint to entirely update an existing order.

    Args:
        order_number (int): The ID of the order to update.
        order_model (OrderModel): The Pydantic model representing the order to update.
        async_session (AsyncSession): The async version of a SQLAlchemy ORM session.

    Raises:
        HTTPException: HTTP 404 Not Found error if the order with the specified ID does not exist.
    """
    order = await aph_delivery_and_release_live_service.retrieve_by_id_async(async_session, order_number)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    await aph_delivery_and_release_live_service.update_async(async_session, order_model)
    await FastAPICache.clear()
    return {"message": f"Order {order_model.order_number} updated successfully"}

# DELETE -----------------------------------------------------------------------


@api_router.delete(
    "/orders/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes an existing order",
    tags=["orders"]
)
async def delete_async(
    order_number: int = Path(..., title="The ID of the order"),
    async_session: AsyncSession = Depends(generate_async_session)
):
    """
    Endpoint to delete an existing order.

    Args:
        order_number (int): The ID of the order to delete.
        async_session (AsyncSession): The async version of a SQLAlchemy ORM session.

    Raises:
        HTTPException: HTTP 404 Not Found error if the order with the specified ID does not exist.
    """
    order = await aph_delivery_and_release_live_service.retrieve_by_id_async(async_session, order_number)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    await aph_delivery_and_release_live_service.delete_async(async_session, order_number)
    await FastAPICache.clear()
    return {"message": f"Order {order_number} deleted successfully"}

    
