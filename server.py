from random import choice
from fastapi import FastAPI
from requests import get, JSONDecodeError, ConnectTimeout

app = FastAPI(
    title="RoPortal",
    description="A very simple rotating Roblox API Proxy",
    version="1.1",
    docs_url="/docs",
    redoc_url=None
)

proxylist = open("proxies.txt", "r").read().strip().split()

@app.get("/")
async def legoproxyHome():
    return {"success": True, "message": "RoPortal is Running!"}

@app.get("/{subdomain}", description="Non-Rotating Proxy Request")
async def proxyRequest(subdomain: str, path: str):
    if path == None: return {"success": False, "message": "RoPortal - Path is a required Query Argument that is missing."}

    try: return get(f'https://{subdomain}.roblox.com/{path}').json()
    except JSONDecodeError: return {"success": False, "message": "RoPortal - Roblox API did not return JSON Data."}

@app.get("/rotate/{subdomain}", description="Rotating Proxy Request")
async def proxyRequest(subdomain: str, path: str):
    if subdomain == None: return {"success": False, "message": "RoPortal - Subdomain is a required Path Argument that is missing."}
    if path == None: return {"success": False, "message": "RoPortal - Path is a required Query Argument that is missing."}
    
    if proxylist == []: return {"success": False, "message": "RoPortal - Proxy IP List is Empty. Please add IPs and Restart RoPortal."}
    proxy = choice(proxylist)
    try: return get(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}).json()
    except JSONDecodeError: return {"success": False, "message": "RoPortal - Roblox API did not return JSON Data."}
    except ConnectTimeout: return {"success": False, "message": f"RoPortal - Proxy Timed Out. Proxy IP: {proxy}"}
    except : return {"success": False, "message": f"RoPortal - Proxy Timed Out. Proxy IP: {proxy}"}
