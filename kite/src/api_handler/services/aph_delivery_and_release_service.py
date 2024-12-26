from typing import Optional
from services import aph_delivery_and_release_live_service, aph_delivery_and_release_batch_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

async def get_dashboard_data(aurora_session: Optional[AsyncSession], redshift_session: Optional[Session], order_number: int):
    """
    Retrieves and combines data from both Live (Aurora) and Batch (Redshift) databases for the dashboard.
    
    Args:
        aurora_session (AsyncSession): Async session for Aurora database.
        redshift_session (Session): Sync session for Redshift database.
    
    Returns:
        A dictionary containing combined data from both databases.
    """
    
     # Combine the data, prioritizing Aurora data
    refined_dashboard_data = {}

    # populating the live data from aurora
    if aurora_session:
        live_data = await aph_delivery_and_release_live_service.retrieve_by_id_async(aurora_session,order_number)
        if  live_data:
            refined_dashboard_data = live_data.model_dump()
        
    # populating the batch data from redshift
    if redshift_session:
        batch_data = await aph_delivery_and_release_batch_service.retrieve_by_id_async(redshift_session,order_number)
        if  batch_data:   
            batch_data_dict = batch_data.model_dump()
        # Only add Redshift data if it's not already present in Aurora data
        for key, value in batch_data_dict.items():
            if key not in refined_dashboard_data or refined_dashboard_data[key] is None:
                refined_dashboard_data[key] = value
    
    return refined_dashboard_data
