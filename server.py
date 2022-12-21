from random import choice
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from requests import get, JSONDecodeError, ConnectTimeout

app = FastAPI(
    title="SimpleLegoProxy",
    description="A VERY simple Roblox Proxy",
    version="1.0",
    docs_url="/docs",
    redoc_url=None
)

proxies_list = open("proxies.txt", "r").read().strip().split()

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

@app.get("rotate/{subdomain}", description="Uses a Random IP")
async def proxyRequest(subdomain: str = None, path: str = None):
    path = path.replace(".", "/")
    if path == None: return {"success": False, "message": "SimpleLegoProxy - API Path is a Required Path Argument that is missing."}
    if subdomain == None: return {"success": False, "message": "SimpleLegoProxy - Subdomain is a Required Path Argument that is missing."}
    if subdomain == None and path == None: return {"success": False, "message": "SimpleLegoProxy - Subdomain and API Path is a Required Path Argument that is missing."}

    if proxies_list == []: return {"success": False, "message": "SimpleLegoProxy - Proxy IP List is Empty. Please add IPs and Restart SimpleLegoProxy."}
    proxy = choice(proxies_list)
    try: return get(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}).json()
    except JSONDecodeError: return {"success": False, "message": "SimpleLegoProxy - Site did not return JSON Data."}
    except ConnectTimeout: return {"success": False, "message": f"SimpleLegoProxy - Proxy Timed Out. Proxy IP: {proxy}"}
