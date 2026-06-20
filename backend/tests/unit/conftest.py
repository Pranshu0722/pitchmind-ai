from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from pitchmind.main import app


@pytest.fixture
async def client() -> AsyncClient:
    # Unit tests don't run the lifespan, so mock Redis on app state
    app.state.redis = AsyncMock()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
