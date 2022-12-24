from os import getenv
from json import loads
from random import choice
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from asyncio import create_task, sleep
from fastapi.responses import FileResponse
from requests import get, post, JSONDecodeError
from requests.exceptions import ConnectionError, ConnectTimeout
load_dotenv(".env")

app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox Proxy for accessing Roblox APIs through HTTPService",
    version="1.4",
    docs_url="/docs",
    redoc_url=None
)

placeId = getenv("placeId")
proxyAuthKey = str(getenv("proxyAuthKey"))
maxRequests = int(getenv("maxRequests"))
webhook = str(getenv("webhook"))
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

def logRequest(method, subdomain, path, response, useragent):
    data = {"content":None,"embeds":[{"title":f"LegoProxy Request Logs ({method})","color":3092790,"fields":[{"name":"Request Endpoint","value":f"**{subdomain}**.roblox.com","inline":True},{"name":"Request Path","value":f"[/{path}](https://users.roblox.com/{path})","inline":True},{"name":"Data Response","value":f"```json\n{response}\n```"}, {"name":"Request User-Agent","value":f"**{useragent}**"}]}],"username":"LegoProxy","avatar_url":"https://cdn.discordapp.com/attachments/1056074242325741578/1056074861690224720/legoproxy.png","attachments":[]}

    if webhook == "": return
    post(getenv("webhook"), json=data)

@app.on_event("startup")
async def on_start():
    create_task(resetRequestsCounter())

@app.get("/")
async def legoproxyHome():
    return {"success": True, "message": "LegoProxy is Running!", "IdLock": idLock, "KeyLock": keyLock, "requestsCreated": requests, "maxRequests": maxRequests}

@app.get("/favicon.ico")
async def legoProxyFavicon():
    return FileResponse("legoproxy.ico")

@app.get("/{subdomain}/{path:path}", description="LegoProxy Roblox GET Request")
@app.post("/{subdomain}/{path:path}", description="LegoProxy Roblox POST Request")
async def robloxRequest(r: Request, subdomain: str, path: str, rotate: bool = False, request: str = None):
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

    if rotate == False:
        try: 
            if r.method == "GET":
                response = get(f'https://{subdomain}.roblox.com/{path}').json()
            if r.method == "POST":
                response = post(f'https://{subdomain}.roblox.com/{path}', json=loads(request)).json()

        except JSONDecodeError: response = {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}
        except ConnectTimeout: response = {"success": False, "message": "LegoProxy - Request Timed Out."}
        except ConnectionError: response = {"success": False, "message": "LegoProxy - Roblox API Endpoint does not exist."}
        logRequest(r.method, subdomain, path, response, r.headers.get("User-Agent"))
        return response
    
    if rotate == True:
        if proxylist == []: return {"success": False, "message": "LegoProxy - Proxy IP List is Empty. Please add IPs and Restart LegoProxy."}
        proxy = choice(proxylist)

        try: 
            if r.method == "GET": 
                response = get(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}).json()
            if r.method == "POST":
                response = post(f'https://{subdomain}.roblox.com/{path}', proxies={"http": f"http://{proxy}"}, json=loads(request)).json()

        except JSONDecodeError: response = {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}
        except ConnectTimeout: response = {"success": False, "message": f"LegoProxy - Proxy Timed Out. Proxy IP: {proxy}"}
        except ConnectionError: response = {"success": False, "message": "LegoProxy - Roblox API Endpoint does not exist."}
        logRequest(r.method, subdomain, path, response, r.headers.get("User-Agent"))
        return response

