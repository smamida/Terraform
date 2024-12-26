
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi import APIRouter, Depends, status, Query
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from data.aurora_order_database import generate_async_session
from data.redshift_order_database import generate_redshift_session
from services import aph_delivery_and_release_service


aph_delivery_and_release_router = APIRouter()

CACHING_TIME_IN_SECONDS = 600

# GET --------------------------------------------------------------------------

@aph_delivery_and_release_router.get(
    "/orders/{order_number}",
    status_code=status.HTTP_200_OK,
    summary="Retrieves a Dashboard data for aph_delivery_and_release dash board",
    tags=["aph_delivery_and_release"]
)
@cache(expire=CACHING_TIME_IN_SECONDS)
async def get_by_id_async(
    order_number: int = Path(..., title="The Id of the order"),
    dashboard: str = Query(..., description="The dashboard type"),
    live: bool = Query(False, description="Query live data from Aurora"),
    batch: bool = Query(False, description="Query batch data from Redshift"),
    aurora_session: AsyncSession = Depends(generate_async_session),
    redshift_session: Session = Depends(generate_redshift_session)
):
    """
    Retrieves dashboard data for a specific order from Aurora and/or Redshift databases.

    This endpoint combines data from live (Aurora) and batch (Redshift) sources for the
    aph_delivery_and_release dashboard. It enforces the following conditions:
    1. The 'dashboard' query parameter must be set to 'aph_delivery_and_release'.
    2. At least one of 'live' or 'batch' parameters must be set to true.

    Args:
        order_number (int): The unique identifier for the order.
        dashboard (str): Must be 'aph_delivery_and_release' for this endpoint.
        live (bool): If True, queries live data from Aurora.
        batch (bool): If True, queries batch data from Redshift.
        aurora_session (AsyncSession): Async session for Aurora database.
        redshift_session (Session): Sync session for Redshift database.

    Returns:
        dict: Combined dashboard data from the specified data sources.

    Raises:
        HTTPException: 
            - 400 if the dashboard parameter is not 'aph_delivery_and_release'.
            - 400 if neither 'live' nor 'batch' is set to true.

    Note:
        This endpoint is cached for CACHING_TIME_IN_SECONDS to improve performance
        for frequently requested data.
    """
    if dashboard != 'aph_delivery_and_release':
        raise HTTPException(
            status_code=400,
            detail="This endpoint is only for the aph_delivery_and_release dashboard"
        )
    if not live and not batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'live' or 'batch' must be set to true"
        )
    aurora_session_arg = aurora_session if live else None
    redshift_session_arg = redshift_session if batch else None
    dashboard_data = await aph_delivery_and_release_service.get_dashboard_data(aurora_session_arg, redshift_session_arg,order_number)
    return dashboard_data
