from typing import Any

import fastapi
import pytest
from fastapi import Depends
from httpx import ASGITransport, AsyncClient

from fastapi_globals.globals import Globals, GlobalsMiddleware

DEPENDS_VAL = "depends-value"
DEFAULT_VAL = "default-value"


g = Globals()  # Own instance to not mix things up
g.set_default("default", "default-value")

app = fastapi.FastAPI(
    title="Globals test app",
)
app.add_middleware(GlobalsMiddleware)


async def set_globals_test():
    g.test = DEPENDS_VAL


async def get_globals_test() -> Any:
    return g.test


@app.get("/test/")
async def app_test_endpoint(value: str = fastapi.Query(...)):
    # Note: This test looks kind of dumb, but makes sure ContextVar.set()
    # and ContextVar.get() work as expected and the class provides easy
    # access to those.
    assert g.test is None
    g.test = value
    assert g.test == await get_globals_test()
    return fastapi.Response(g.test, media_type="text/plain")


@app.get("/test-default/")
async def app_default_endpoint():
    return fastapi.Response(g.default, media_type="text/plain")


@app.get("/test-depends/", dependencies=[Depends(set_globals_test)])
async def app_test_endpoint_with_depends():
    assert g.test == DEPENDS_VAL
    return fastapi.Response(g.test, media_type="text/plain")


@pytest.fixture
def test_client():
    return AsyncClient(
        base_url='http://test',
        transport=ASGITransport(app=app),
    )


@pytest.mark.unit
@pytest.mark.anyio
@pytest.mark.parametrize(
    "value",
    [
        "test-value",
        "other-value",
    ],
)
async def test_globals_access(test_client, value: str):
    response = await test_client.get(
        "/test/", params={
            "value": value,
        },
    )

    assert response.text == value


@pytest.mark.unit
@pytest.mark.anyio
async def test_globals_access_for_depends(test_client):
    response = await test_client.get("/test-depends/")

    assert response.text == DEPENDS_VAL


@pytest.mark.unit
@pytest.mark.anyio
async def test_globals_default(test_client):
    response = await test_client.get("/test-default/")

    assert response.text == DEFAULT_VAL


@pytest.mark.unit
def test_globals_defaults_can_only_be_set_once():
    assert "default" in g._defaults
    g.set_default("default", DEFAULT_VAL)  # ok cause it's the same value
    with pytest.raises(RuntimeError):
        g.set_default("default", "other-value")
