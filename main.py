from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import FileResponse, RedirectResponse

import json
from httpx import AsyncClient
from base64 import b64encode
from json.decoder import JSONDecodeError
from httpx._exceptions import ConnectError, ConnectTimeout, RequestError

def getConfig():
    with open('./core/config.json', 'r') as f:
        config = json.load(f)
        return config

app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox API Proxy for accessing Roblox APIs through HTTPService",
    version="v1.7",
    docs_url=None,
    redoc_url=None
)

cacheDict = {}
proxylist = open("./core/assets/proxies.txt", "r").read().split()

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

    if config["blacklistedSubdomains"].__contains__(subdomain):
        return {
            "success": False,
            "message": "The Roblox API is Blacklisted to this LegoProxy Server."
        }
    
    if config["placeId"] != 0 and request.headers.get("Roblox-Id") != config["placeId"]:
        return {
            "success": False,
            "message": "This proxy is only accepting requests from a Roblox Game."
        }

    if config["proxyAuthKey"] != "" and request.headers.get("LP-AuthKey")!= config["proxyAuthKey"]:
        return {
            "success": False,
            "message": "This proxy requires an Authentication Key to complete a Request."
        }

    try:
        async with AsyncClient(proxies={"http://": f"http://{proxy}"}) as cli:
            if request.query_params == None:
                req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}", data=data)
            else:
                req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}?{request.query_params}", data=data)

            res = await cli.send(req)
            response = res.json()

    except JSONDecodeError: 
        response = {
            "success": False,
            "message": "The Roblox API did not return any JSON Data."
        }

    except ConnectTimeout: 
        response = {
            "success": False,
            "message": f"Connection Timeout. Proxy IP {proxy} could be a dead proxy."
        }

    except ConnectError: 
        response = {
            "success": False,
            "message": "The Roblox API Subdomain does not exist."
        }
    
    except RequestError:
        response = {
            "success": False,
            "message": "Failed to send a Request to the Roblox API."
        }

    return response



