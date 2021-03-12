# conftest.py

import asyncio
import pytest
import httpx

HOSTNAME = 'http://PhaseOne.local:3300'
BASE_HEADERS = {'Host': 'PhaseOne.local.'}

@pytest.fixture(scope="module")
def client():
    c = httpx.AsyncClient(base_url=HOSTNAME, headers=BASE_HEADERS)
    yield c
    asyncio.run(c.aclose())


def pytest_configure():
    pytest.session = None