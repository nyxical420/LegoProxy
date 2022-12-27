from random import randint, random
from asyncio import create_task
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse

from core.conf import LegoProxyConfig
from core.auth.dashboard import validate_credentials
from core.request import proxyRequest, resetRequestsCounter
config = LegoProxyConfig()

config.placeId = None
config.proxyAuthKey = None
config.maxRequests = 10
config.webhookUrl = "https://discord.com/api/webhooks/1057149841790214236/JdARQz8QaQUHdZzDl_h7SBGjnowXbMZEb5bt_N7wBoJ9eQQTm3kxHm-f1bxtbcQV2Ifk"

config.rotate = True
config.dashboardEnabled = True
config.dashboardUsername = "tsuki"
config.dashboardPassword = "tsukiaoki"

app = FastAPI(
    title="LegoProxy",
    description="A rotating Roblox Proxy for accessing Roblox APIs through HTTPService",
    version="1.5",
    docs_url="/docs",
    redoc_url=None
)

redirectAuth = ""

def generateAuth():
    temp = ""
    for i in range(32):
        random_char = chr(randint(ord('a'), ord('z'))) if random() < 0.5 else str(randint(0, 9))
        temp += random_char

@app.on_event("startup")
async def on_start():
    create_task(resetRequestsCounter())

## LegoProxy Dashboard

@app.get("/")
@app.post("/")
async def legoProxyHome(r: Request, username: str = Form(None), password: str = Form(None)):
    if not config.dashboardEnabled: return "Dashboard is Disabled."

    if r.headers.get("RedirectAuth") == redirectAuth:
        generateAuth()
        return FileResponse("./templates/dashboard.html")

    if username == None: return FileResponse("./templates/login.html")
    if password == None: return FileResponse("./templates/login.html")
    authenticated = validate_credentials(username.lower(), password.lower(), config)

    if authenticated:
        return FileResponse("./templates/dashboard.html")
    else:
        return FileResponse("./templates/login.html")

@app.get("/logs")
async def getLogs():
    return HTMLResponse(proxyRequest.log)

@app.post("/saveconf")
async def saveConfig(placeId: int = Form(None), maxRequests: int = Form(100), proxyAuthKey: str = Form(None), webhook: str = Form(None), username: str = Form(None), password: str = Form(None)):
    try: authenticated = validate_credentials(username.lower(), password.lower(), config)
    except AttributeError: authenticated = False
        
    if authenticated:
        config.placeId = placeId
        config.maxRequests = maxRequests
        config.proxyAuthKey = proxyAuthKey
        config.webhookUrl = webhook
        return RedirectResponse("/", headers={"RedirectAuth": redirectAuth})
    else:
        return RedirectResponse("/")

@app.get("/static/{filepath:path}")
async def getFile(filepath: str):
    return FileResponse(f'static/{filepath}')

@app.get("/favicon.ico")
async def legoProxyFavicon():
    return FileResponse("legoproxy.ico")

## Roblox Proxy

@app.get("/{subdomain}/{path:path}", description="LegoProxy Roblox GET Request")
@app.post("/{subdomain}/{path:path}", description="LegoProxy Roblox POST Request")
@app.patch("/{subdomain}/{path:path}", description="LegoProxy Roblox PATCH Request")
@app.delete("/{subdomain}/{path:path}", description="LegoProxy Roblox DELETE Request")
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
