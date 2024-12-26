# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from mangum import Mangum
from routes import aph_delivery_and_release_route, order_route

"""
FastAPI app initialization
"""

@asynccontextmanager
async def lifespan_context_manager(_):
    """
    Context manager for the FastAPI app lifespan.

    Initializes  FastAPICache with an InMemoryBackend for the duration of the app's lifespan.
    """
    FastAPICache.init(InMemoryBackend())
    yield

app = FastAPI(lifespan=lifespan_context_manager,
              title="gilead-api-restful",
              description="🧪 Proof of Concept for a Gilead order data processing Solution",
              version="1.0.0",)

#app.include_router(order_route.api_router)
app.include_router(aph_delivery_and_release_route.aph_delivery_and_release_router)

handler = Mangum(app)

