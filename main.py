from asyncio import create_task
from random import randint, random
from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse, Response

from base64 import b64encode

from core.conf import LegoProxyConfig
from core.auth.dashboard import validate_credentials
from core.request import proxyRequest, resetRequestsCounter

config = LegoProxyConfig()

config.caching = False
config.maxRequests = 50
config.dashboardUsername = "admin"
config.dashboardPassword = "admin"

redirectAuth = ""

app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox Proxy for accessing Roblox APIs through HTTPService",
    version="1.6",
    docs_url=None,
    redoc_url=None
)

for i in range(32): 
    redirectAuth += chr(randint(ord('a'), ord('z'))) if random() < 0.5 else str(randint(0, 9))
        
@app.on_event("startup")
async def on_start():
    create_task(resetRequestsCounter())

## LegoProxy Dashboard

@app.get("/")
@app.post("/")
async def legoProxyHome(r: Request, username: str = Form(""), password: str = Form("")):
    authCookie = r.cookies.get("legoproxy_auth")

    if authCookie != None:
        if authCookie.__contains__(b64encode(config.dashboardUsername.encode("ascii")).decode("utf-8") + "." + b64encode(config.dashboardPassword.encode("ascii")).decode("utf-8")):
            return FileResponse("./templates/dashboard.html")

    if username == "": return FileResponse("./templates/login.html")
    if password == "": return FileResponse("./templates/login.html")
    authenticated = validate_credentials(username, password, config)

    if authenticated:
        response = RedirectResponse("/")
        authcookie = b64encode(username.encode("ascii")).decode("utf-8") + "." + b64encode(password.encode("ascii")).decode("utf-8")
        response.set_cookie("legoproxy_auth", value=f"{authcookie}", expires=1800)
        response.set_cookie("legoproxy_username", value=f"{username}", expires=1800)
        return response

    if authCookie == None and not authenticated:
        return FileResponse("./templates/login.html")

    # Logs the user out of the Dashboard if it does not meet any conditions.
    # Possible Reason: Administrator changed dashboard credentials
    return RedirectResponse("/logout")

@app.get("/logout")
@app.post("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie("legoproxy_auth")
    response.delete_cookie("legoproxy_username")
    return response


@app.get("/docs")
@app.get("/documentation")
async def documentation():
    return FileResponse("./templates/docs.html")


@app.get("/logs")
async def getLogs():
    return HTMLResponse(proxyRequest.log)

@app.get("/getconf")
async def getConfig():
    return {
        "placeId": config.placeId,
        "maxRequests": config.maxRequests,
        "proxyAuthKey": config.proxyAuthKey,
        "cacheExpiry": config.expiry
    }

@app.post("/saveconf")
async def saveConfig(r: Request):
    data = await r.json()

    authCookie = r.cookies.get("legoproxy_auth")
    if authCookie.__contains__(b64encode(config.dashboardUsername.encode("ascii")).decode("utf-8") + "." + b64encode(config.dashboardPassword.encode("ascii")).decode("utf-8")):
        if data["placeId"] != 0: config.placeId = data["placeId"]
        if data["maxRequests"] != 0: config.maxRequests = data["maxRequests"]
        if data["proxyAuthKey"] != "": config.proxyAuthKey = data["proxyAuthKey"]
        if data["cacheExpiry"] != 0: config.expiry = data["cacheExpiry"]
        return "Configuration Saved"

@app.get("/static/{filepath:path}")
async def getFile(filepath: str):
    return FileResponse(f'static/{filepath}')

@app.get("/favicon.ico")
async def legoProxyFavicon():
    return FileResponse("assets/legoproxy.ico")

## Roblox Proxy

@app.get("/{subdomain}/{path:path}", description="LegoProxy Roblox GET Request")
@app.post("/{subdomain}/{path:path}", description="LegoProxy Roblox POST Request")
@app.patch("/{subdomain}/{path:path}", description="LegoProxy Roblox PATCH Request")
@app.delete("/{subdomain}/{path:path}", description="LegoProxy Roblox DELETE Request")
async def robloxRequest(r: Request, subdomain: str, path: str, request: dict = Body({})):
    legoProxy = proxyRequest()
    legoProxy.subdomain = subdomain
    legoProxy.path = path
    legoProxy.data = request
    legoProxy.method = r.method
    
    legoProxy.authKey = r.headers.get("LP-AuthKey")
    legoProxy.authRobloxId = r.headers.get("Roblox-Id")
    legoProxy.authUserAgent = r.headers.get("User-Agent")

    return await legoProxy.request(config=config)
 
