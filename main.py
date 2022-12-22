from json import loads
from random import choice
from fastapi import FastAPI, Request
from requests import get, post, JSONDecodeError, ConnectTimeout

app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox Proxy for accessing Roblox APIs through HTTPService",
    version="1.2",
    docs_url="/docs"
)

proxylist = open("proxies.txt", "r").read().strip().split()

# If the placeId variable is set, all incoming requests will be blocked unless the request is from a game.
# placeId 変数が設定されている場合、リクエストがゲームからのものでない限り、すべての着信リクエストがブロックされます。
placeId = 0

@app.get("/")
async def legoproxyHome():
    return {"success": True, "message": "LegoProxy is Running!"}

@app.get("/{subdomain}/{path:path}", description="Non-Rotating Proxy GET Request")
@app.post("/{subdomain}/{path:path}", description="Non-Rotating Proxy POST Request")
async def proxyRequest(r: Request, subdomain: str, path: str, request: str = None):
    if placeId != 0: 
        if r.headers.get("Roblox-Id") != str(placeId):
            return {"success": False, "message": "LegoProxy - This proxy is Game Locked."}

    if path == None: return {"success": False, "message": "LegoProxy - Endpoint is a required Query Argument that is missing."}

    try: 
        if r.method == "GET":
            return get(f'https://{subdomain}.roblox.com/{path}').json()
        if r.method == "POST":
            return post(f'https://{subdomain}.roblox.com/{path}', json=loads(request)).json()

    except JSONDecodeError: return {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}

@app.get("/rotate/{subdomain}/{path:path}", description="Rotating Proxy GET Request")
@app.post("/rotate/{subdomain}/{path:path}", description="Rotating Proxy POST Request")
async def proxyRequest_rotating(r: Request, subdomain: str, path: str, request: str = None):
    if placeId != 0: 
        if r.headers.get("Roblox-Id") != str (placeId):
            return {"success": False, "message": "LegoProxy - This Proxy is Game Locked."}

    if subdomain == None: return {"success": False, "message": "LegoProxy - Subdomain is a required Path Argument that is missing."}
    if path == None: return {"success": False, "message": "LegoProxy - Endpoint is a required Query Argument that is missing."}
    
    if proxylist == []: return {"success": False, "message": "LegoProxy - Proxy IP List is Empty. Please add IPs and Restart LegoProxy."}
    proxy = choice(proxylist)
    
    try: 
        if r.method == "GET":
            return get(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}).json()
        if r.method == "POST":
            return post(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}, json=loads(request)).json()

    except JSONDecodeError: return {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}
    except ConnectTimeout: return {"success": False, "message": f"LegoProxy - Proxy Timed Out. Proxy IP: {proxy}"}
