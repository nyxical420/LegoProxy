from fastapi import FastAPI
from requests import get, JSONDecodeError

app = FastAPI()

@app.get("/")
async def proxyRequest(subdomain: str = None, path: str = None):
    if subdomain == None and path == None: return {"success": True, "message": "SimpleLegoProxy is Running!"}

    if path == None: return {"success": False, "message": "SimpleLegoProxy - API Path is a Required Query Argument that is missing."}
    if subdomain == None: return {"success": False, "message": "SimpleLegoProxy - Subdomain is a Required Query Argument that is missing."}
    try: return get(f'https://{subdomain}.roblox.com/{path}').json()
    except JSONDecodeError: return {"success": False, "message": "SimpleLegoProxy - Site did not return JSON Data."}
