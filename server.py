from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from requests import get, JSONDecodeError

app = FastAPI(
    title="SimpleLegoProxy",
    description="A VERY simple Roblox Proxy",
    version="1.0",
    docs_url="/docs",
    redoc_url=None
)

@app.get("/")
async def legoproxyHome():
    return RedirectResponse("https://github.com/PyTsun/SimpleLegoProxy")

@app.get("/{subdomain}")
async def proxyRequest(subdomain: str = None, path: str = None):
    path = path.replace(".", "/")
    if path == None: return {"success": False, "message": "SimpleLegoProxy - API Path is a Required Path Argument that is missing."}
    if subdomain == None: return {"success": False, "message": "SimpleLegoProxy - Subdomain is a Required Path Argument that is missing."}
    if subdomain == None and path == None: return {"success": False, "message": "SimpleLegoProxy - Subdomain and API Path is a Required Path Argument that is missing."}

    try: return get(f'https://{subdomain}.roblox.com/{path}').json()
    except JSONDecodeError: return {"success": False, "message": "SimpleLegoProxy - Site did not return JSON Data."}
