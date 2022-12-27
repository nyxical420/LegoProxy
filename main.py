from asyncio import create_task
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse

from core.conf import LegoProxyConfig
from core.auth.dashboard import validate_credentials
from core.request import proxyRequest, resetRequestsCounter
config = LegoProxyConfig()

config.placeId = None
config.proxyAuthKey = None
config.maxRequests = 10

config.rotate = True
config.dashboardEnabled = True

app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox Proxy for accessing Roblox APIs through HTTPService",
    version="1.5",
    docs_url="/docs",
    redoc_url=None
)

logs = "Hello, World!"

@app.on_event("startup")
async def on_start():
    create_task(resetRequestsCounter())

## LegoProxy Dashboard

@app.get("/")
@app.post("/")
async def legoProxyHome(username: str = Form(None), password: str = Form(None)):
    if not config.dashboardEnabled: return "Dashboard is Disabled."

    if username == None: return FileResponse("./templates/login.html")
    if password == None: return FileResponse("./templates/login.html")
    authenticated = validate_credentials(username.lower(), password.lower())

    if authenticated:
        return FileResponse("./templates/dashboard.html")
    else:
        return FileResponse("./templates/login.html")

@app.get("/logs")
async def getLogs():
    return logs

@app.get("/saveconf")
@app.post("/saveconf")
async def saveConfig():
    return "Not Available"


@app.get("/static/{filepath:path}")
async def getFile(filepath: str):
    return FileResponse(f'static/{filepath}')

@app.get("/favicon.ico")
async def legoProxyFavicon():
    return FileResponse("legoproxy.ico")

## Roblox Proxy

@app.get("/{subdomain}/{path:path}", description="LegoProxy Roblox GET Request")
@app.post("/{subdomain}/{path:path}", description="LegoProxy Roblox POST Request")
async def robloxRequest(r: Request, subdomain: str, path: str, request: str = None):
    legoProxy = proxyRequest()
    legoProxy.subdomain = subdomain
    legoProxy.path = path
    legoProxy.rotate = config.rotate
    legoProxy.data = request
    legoProxy.method = r.method
    
    legoProxy.authKey = r.headers.get("LP-AuthKey")
    legoProxy.authRobloxId = r.headers.get("Roblox-Id")
    legoProxy.authUserAgent = r.headers.get("User-Agent")

    return await legoProxy.request(config=config)
