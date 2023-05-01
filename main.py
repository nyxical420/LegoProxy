from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse

import json
from uvicorn import run
from random import choice
from threading import Thread
from time import time, sleep
from base64 import b64encode
from httpx import AsyncClient
from core.packages.logging import log
from json.decoder import JSONDecodeError
from httpx._exceptions import ConnectError, ConnectTimeout, RequestError

app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox API Proxy for accessing Roblox APIs through HTTPService",
    version="v2-bugfix",
    docs_url=None,
    redoc_url=None
)

proxylist = open("./core/assets/proxies.txt", "r").read().split()
blacklist = open("./core/blacklist.txt", "r").read().split()
gameblacklist = open("./core/blacklist_games.txt", "r").read().split()

def getConfig():
    with open('./core/config.json', 'r') as f:
        config = json.load(f)
        return config

reqTime = 60
reqLimit = 256
blockTime = 43200

users = {}
blacklisted = {}

@app.middleware("http")
async def RateLimiter(request: Request, call_next):
    proxyIP = request.headers.get("X-Forwarded-For")
    placeId = request.headers.get("Roblox-Id")

    log(request.method, proxyIP, 0, request.url.path, request.query_params)

    def convertTS(time_left):
        hours, remainder = divmod(time_left, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02} Hours {minutes:02} Minutes {seconds:02} Seconds"

    if proxyIP in blacklist:
        log(request.method, proxyIP, 3, request.url.path, request.query_params)
        return JSONResponse(content={"success": False, "message": f"You are permanently blacklisted from using this LegoProxy Server."}, status_code=401)

    if placeId in gameblacklist:
        log(request.method, proxyIP, 3, request.url.path, request.query_params)
        return JSONResponse(content={"success": False, "message": f"Your Roblox Game is permanently blacklisted from using this LegoProxy Server."}, status_code=401)

    if placeId != None:
        if placeId in gameblacklist:
            log(request.method, proxyIP, 3, request.url.path, request.query_params)
            return JSONResponse(content={"success": False, "message": f"Your Roblox Game is permanently blacklisted from using this LegoProxy Server."}, status_code=401)

        if not placeId in users:
            users[placeId] = {"count": 0, "time": time()}
        else:
            if time() - users[placeId]["time"] > reqTime:
                users.pop(placeId, None)
            else:
                if users[placeId]["count"] >= reqLimit:
                    if placeId not in blacklisted:
                        blacklisted[placeId] = time() + blockTime
                    users[placeId]["count"] = 0

            users[placeId]["count"] += 1

        if placeId in blacklisted:
            remaining_time = int(blacklisted[placeId] - time())

            if remaining_time <= 0:
                del blacklisted[placeId]
            else:
                log(request.method, proxyIP, 3, request.url.path, request.query_params)
                return JSONResponse(content={"success": False, "message": f"You are temporarily blacklisted from using this LegoProxy Server for {convertTS(remaining_time)}."}, status_code=429)

    else:
        if not proxyIP in users:
            users[proxyIP] = {"count": 0, "time": time()}
        else:
            if time() - users[proxyIP]["time"] > reqTime:
                users.pop(proxyIP, None)
            else:
                if users[proxyIP]["count"] >= reqLimit:
                    if proxyIP not in blacklisted:
                        blacklisted[proxyIP] = time() + blockTime
                    users[proxyIP]["count"] = 0

            try: users[proxyIP]["count"] += 1
            except KeyError: pass

        if proxyIP in blacklisted:
            remaining_time = int(blacklisted[proxyIP] - time())

            if remaining_time <= 0:
                del blacklisted[proxyIP]
            else:
                log(request.method, proxyIP, 3, request.url.path, request.query_params)
                return JSONResponse(content={"success": False, "message": f"You are temporarily blacklisted from using this LegoProxy Server for {convertTS(remaining_time)}."}, status_code=429)

    response = await call_next(request)
    return response

def cleanup_users():
    while True:
        for proxyIP, data in list(users.items()):
            if time() - data["time"] > reqTime:
                del users[proxyIP]

        sleep(1)

@app.on_event("startup")
async def startup_event():
    thread = Thread(target=cleanup_users)
    thread.daemon = True
    thread.start()

@app.get("/")
@app.post("/")
async def proxyHome(
    request: Request,
    password: str = Form("")
):
    config = getConfig()
    authenticationCookie = request.cookies.get("LP_Auth")

    if authenticationCookie != None:
        if authenticationCookie.__contains__(b64encode(config["password"].encode("ascii")).decode("utf-8")):
            return FileResponse("./core/pages/dashboard.html")
        
    if password == "":
        return FileResponse("./core/pages/login.html")

    if authenticationCookie == None:
        if str(config["password"]) == str(password):
            response = RedirectResponse("/")
            authcookie = b64encode(password.encode("ascii")).decode("utf-8")
            response.set_cookie("LP_Auth", value=f"{authcookie}", max_age=3600)
            return response

        if str(config["password"]) != str(password):
            return FileResponse("./core/pages/login.html")
    
    return RedirectResponse("/logout")

@app.get("/logout")
@app.post("/logout")
async def logoutProxy():
    response = RedirectResponse("/")
    response.delete_cookie("LP_Auth")
    return response

@app.get("/getconf")
async def getConfiguration():
    config = getConfig()

    return {
        "placeId": config["placeId"],
        "proxyAuthKey": config["proxyAuthKey"],
        "cacheExpiry": config["cacheExpiry"]
    }

@app.post("/saveconf")
async def saveConfig(r: Request):
    config = getConfig()
    data = await r.json()

    authenticationCookie = r.cookies.get("LP_Auth")
    if authenticationCookie.__contains__(b64encode(config["password"].encode("ascii")).decode("utf-8")):
        config["placeId"] = data["placeId"]
        config["cacheExpiry"] = data["cacheExpiry"]
        config["proxyAuthKey"] = data["proxyAuthKey"]

        with open('./core/config.json', 'w+') as f:
            json.dump(config, f, indent=4)

        return "Configuration Saved"

@app.get("/static/{filepath:path}")
async def getFile(filepath: str):
    return FileResponse(f'./core/static/{filepath}')

@app.get("/{subdomain}/{path:path}", description="LegoProxy Roblox GET Request")
@app.post("/{subdomain}/{path:path}", description="LegoProxy Roblox POST Request")
@app.patch("/{subdomain}/{path:path}", description="LegoProxy Roblox PATCH Request")
@app.delete("/{subdomain}/{path:path}", description="LegoProxy Roblox DELETE Request")
async def requestProxy(
    request: Request,
    subdomain: str,
    path: str,
    data: dict = Body({})
): 
    config = getConfig()
    proxyIP = request.headers.get("X-Forwarded-For")

    if config["blacklistedSubdomains"].__contains__(subdomain):
        log(request.method, proxyIP, 2, request.url.path, request.query_params)

        return {
            "success": False,
            "message": "This LegoProxy Server is Blocking this Roblox API."
        }
    
    if config["placeId"] != 0 and request.headers.get("Roblox-Id") != config["placeId"]:
        log(request.method, proxyIP, 2, request.url.path, request.query_params)
        return {
            "success": False,
            "message": "This LegoProxy Server is only accepting requests through a Roblox Game."
        }

    if config["proxyAuthKey"] != "" and request.headers.get("LP-AuthKey")!= config["proxyAuthKey"]:
        log(request.method, proxyIP, 2, request.url.path, request.query_params)
        return {
            "success": False,
            "message": "This LegoProxy Server requires an Authorization Key to complete an Proxy Request."
        }

    try:
        if config["proxyRotate"] == True:
            proxy = choice(proxylist)
            async with AsyncClient(proxies={"http://": f"http://{proxy}", "https://": f"https://{proxy}"}) as cli:
                if request.query_params == None:
                    req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}", json=data)
                else:
                    req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}?{request.query_params}", json=data)

                res = await cli.send(req)
                response = res.json()
        
        else:
            async with AsyncClient() as cli:
                if request.query_params == None:
                    req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}", json=data)
                else:
                    req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}?{request.query_params}", json=data)

                res = await cli.send(req)
                response = res.json()

    except JSONDecodeError: 
        log(request.method, proxyIP, 2, request.url.path, request.query_params)
        response = {
            "success": False,
            "message": "The Roblox API did not return any JSON Data."
        }

    except ConnectTimeout: 
        log(request.method, proxyIP, 2, request.url.path, request.query_params)
        response = {
            "success": False,
            "message": f"Connection Timeout. Proxy IP {proxy} could be a dead proxy."
        }

    except ConnectError: 
        log(request.method, proxyIP, 2, request.url.path, request.query_params)
        response = {
            "success": False,
            "message": "The Roblox API Subdomain does not exist."
        }
    
    except RequestError:
        log(request.method, proxyIP, 2, request.url.path, request.query_params)
        response = {
            "success": False,
            "message": "Failed to send a Request to the Roblox API."
        }

    log(request.method, proxyIP, 1, request.url.path, request.query_params)
    return response

if __name__ == "__main__":
    print("LegoProxy Started!")
    run("main:app", host="127.0.0.1", port=443, reload=True, log_level="warning")
