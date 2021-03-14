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
    try:
        asyncio.run(c.aclose())
    except:
        pass


def pytest_configure():
    pytest.session = None
    pytest.initial_props = None