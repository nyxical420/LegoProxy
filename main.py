from os import getenv
from json import loads
from random import choice
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from asyncio import create_task, sleep
from fastapi.responses import FileResponse
from requests import get, post, JSONDecodeError, ConnectTimeout
load_dotenv(".env")


app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox Proxy for accessing Roblox APIs through HTTPService",
    version="1.3",
    docs_url="/docs"
)

placeId = getenv("placeId")
proxyAuthKey = getenv("proxyAuthKey")
maxRequests = int(getenv("maxRequests"))
idLock = False if placeId == "" else True
keyLock = False if proxyAuthKey == "" else True
proxylist = open("proxies.txt", "r").read().strip().split()

global requests
requests = 0

async def resetRequestsCounter():
    global requests
    while True: 
        await sleep(60)
        requests -= requests
        #print("Requests per minute (RPM) restarted!")


@app.on_event("startup")
async def on_start():
    create_task(resetRequestsCounter())

@app.get("/")
async def legoproxyHome():
    return {"success": True, "message": "LegoProxy is Running!", "IdLock": idLock, "KeyLock": keyLock, "requestsCreated": requests, "maxRequests": maxRequests}

@app.get("/favicon.ico")
async def legoProxyFavicon():
    return FileResponse("legoproxy.ico")

@app.get("/{subdomain}/{path:path}", description="Non-Rotating Proxy GET Request")
@app.post("/{subdomain}/{path:path}", description="Non-Rotating Proxy POST Request")
async def proxyRequest(r: Request, subdomain: str, path: str, request: str = None):
    global requests
    if requests >= maxRequests:
        return {"success": False, "message": "LegoProxy - Max Requests has been reached. Please try again later!"}
    
    if idLock: 
        if r.headers.get("Roblox-Id") != str(placeId):
            return {"success": False, "message": "LegoProxy - This proxy is only accepting requests from a Roblox Game."}
    
    if keyLock:
        if r.headers.get("LP-AuthKey") != proxyAuthKey:
            return {"success": False, "message": "LegoProxy - This proxy requires an Authentication Key."}

    requests += 1

    try: 
        if r.method == "GET":
            return get(f'https://{subdomain}.roblox.com/{path}').json()
        if r.method == "POST":
            return post(f'https://{subdomain}.roblox.com/{path}', json=loads(request)).json()

    except JSONDecodeError: return {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}
    except ConnectTimeout: return {"success": False, "message": "LegoProxy - Request Timed Out."}
    except ConnectionError: return {"success": False, "message": "LegoProxy - Roblox API Endpoint does not exist."}

@app.get("/rotate/{subdomain}/{path:path}", description="Rotating Proxy GET Request")
@app.post("/rotate/{subdomain}/{path:path}", description="Rotating Proxy POST Request")
async def proxyRequest_rotating(r: Request, subdomain: str, path: str, request: str = None):
    global requests
    if requests > maxRequests:
        return {"success": False, "message": "LegoProxy - Max Requests has been reached. Please try again later!"}
        
    if idLock: 
        if r.headers.get("Roblox-Id") != str(placeId):
            return {"success": False, "message": "LegoProxy - This proxy is only accepting requests from a Roblox Game."}
    
    if keyLock:
        if r.headers.get("LP-AuthKey") != proxyAuthKey:
            return {"success": False, "message": "LegoProxy - This proxy requires an Authentication Key."}

    if subdomain == None: return {"success": False, "message": "LegoProxy - Subdomain is a required Path Argument that is missing."}
    
    if proxylist == []: return {"success": False, "message": "LegoProxy - Proxy IP List is Empty. Please add IPs and Restart LegoProxy."}
    proxy = choice(proxylist)
    
    try: 
        if r.method == "GET": 
            return get(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}).json()
        if r.method == "POST":
            return post(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}, json=loads(request)).json()
        requests += 1

    except JSONDecodeError: return {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}
    except ConnectTimeout: return {"success": False, "message": f"LegoProxy - Proxy Timed Out. Proxy IP: {proxy}"}
    except ConnectionError: return {"success": False, "message": "LegoProxy - Roblox API Endpoint does not exist."}

