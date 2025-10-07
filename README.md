# `fastapi-globals`

Allows you to use request global values. Can be used to store request speficic data, like state, database
connection, etc.

## Installation

Just use `pip install fastapi-globals` to install the library.

**Note:** `fastapi-globals` is compatible with `fastapi` versions `0.100.0` and later on
Python `3.10`, `3.11`, `3.12` and `3.13`. This is also ensured running all tests on all those versions
using `tox`.

## Setup

Add the `GlobalsMiddleware` to your app:
```python
app = fastapi.FastAPI(
    title="Your app API",
)
app.add_middleware(GlobalsMiddleware)  # <-- This line is necessary
```

## Usage

Import `g` and then access (set/get) attributes of it:
```python
from fastapi_globals import g


g.foo = "foo"

# In some other code
assert g.foo == "foo"
```

Best way to utilize the global `g` in your code is to set the desired
value in a FastAPI dependency, like so:
```python
async def set_global_foo() -> None:
    g.foo = "foo"


@app.get("/test/", dependencies=[Depends(set_global_foo)])
async def test():
    assert g.foo == "foo"
```

## Default values

You may use `g.set_default("name", some_value)` to set a default value
for a global variable. This default value will then be used instead of `None`
when the variable is accessed before it was set.

Note that default values should only be set at startup time, never
inside dependencies or similar. Otherwise you may run into the issue that
the value was already used any thus have a value of `None` set already, which
would result in the default value not being used.
