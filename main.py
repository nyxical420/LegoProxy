from fastapi import FastAPI, Request, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from uvicorn import run
from random import choice
from random import randint
from json import load, dump
from threading import Thread
from time import time, sleep
from os import getenv as env
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, init
from shortuuid import ShortUUID
from cachetools import TTLCache
from httpx import AsyncClient, post
from asyncio import sleep as asyncsleep

from json.decoder import JSONDecodeError
from httpx._exceptions import ConnectError, RequestError
load_dotenv(".env")

app = FastAPI(
    title="LegoProxy",
    description="A Roblox API And Webhook Proxy for Roblox HTTPService",
    version="v2.1",
    docs_url=None,
    redoc_url=None
)

class Logging:
    init(autoreset=True)

    @staticmethod
    def requestLog(array):
        method, ip, id, status, path, query = array[0], array[1], array[2], array[3], array[4], array[5]
        color = {0: Fore.LIGHTBLUE_EX, 1: Fore.LIGHTGREEN_EX, 2: Fore.LIGHTYELLOW_EX, 3: Fore.LIGHTRED_EX}
        icon = {0: "-->", 1: "<--", 2: "-!-", 3: "-X-"}

        if query is not None:
            path += f"?{query}"

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.LIGHTBLACK_EX}{date}{Fore.RESET} {color[status]}{method}\t{ip} ({id}) {icon[status]} {path}".replace("(None)", ""))

    @staticmethod
    def proxyLog(text, color=0):
        if color == 0:
            color = Fore.LIGHTBLUE_EX
            type = "INFO"
        elif color == 1:
            color = Fore.LIGHTRED_EX
            type = "ERROR"

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.LIGHTBLACK_EX}{date}{Fore.RESET} {color}{type}\t{Fore.RESET}{text}")

def config():
    with open('./core/config.json', 'r') as f:
        configData = load(f)
    return configData

users = {}
blacklisted = {}

relay = {
    "connections": {},
    "responses": {}
}

responseTime = [0]
sets = 30

cache = TTLCache(
    maxsize=config()["config"]["proxy"]["cacheMaxSize"],
    ttl=config()["config"]["proxy"]["cacheTTL"]
)

@app.middleware("http")
async def rateLimiter(request: Request, callNext):
    ip, id = request.headers.get("X-Forwarded-For"), request.headers.get("Roblox-Id")
    Logging.requestLog([request.method, ip, id, 0, request.url.path, request.query_params])

    def convertTime(timeLeft):
        hours, remainder = divmod(timeLeft, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02} Hours {minutes:02} Minutes {seconds:02} Seconds"

    proxyConfig = config()

    if ip in proxyConfig["config"]["blocking"]["ips"]:
        Logging.requestLog([request.method, ip, id, 3, request.url.path, request.query_params])
        return JSONResponse(
            content={
                "success": False,
                "message": f"This IP is being blocked by the LegoProxy Server."
            },
            status_code=401
        )

    if id in proxyConfig["config"]["blocking"]["ids"]:
        Logging.requestLog([request.method, ip, id, 3, request.url.path, request.query_params])
        return JSONResponse(
            content={
                "success": False,
                "message": f"This Roblox Game is being blocked by the Legoproxy Server."
            },
            status_code=401
        )
    
    if id is not None:
        if not id in users:
            users[id] = {"count": 0, "time": time()}
        else:
            if time() - users[id]["time"] > proxyConfig["config"]["proxy"]["requestTime"]:
                users.pop(id, None)
            else:
                if users[id]["count"] >= proxyConfig["config"]["proxy"]["requestLimit"]:
                    if id not in blacklisted:
                        blacklisted[id] = time() + proxyConfig["config"]["blocking"]["blockTime"]
                    users[id]["count"] = 0

                try:
                    users[id]["count"] += 1
                except KeyError:
                    pass

        if id in blacklisted:
            remainingTime = int(blacklisted[id] - time())

            if remainingTime <= 0:
                del blacklisted[id]
            else:
                Logging.requestLog([request.method, ip, id, 3, request.url.path, request.query_params])
                return JSONResponse(
                    content={
                        "success": False,
                        "message": f"This Roblox Game is temporarily blocked by the LegoProxy Server for {convertTime(remainingTime)}."
                    }, 
                    status_code=429
                )
    
    else:
        if not ip in users:
            users[ip] = {"count": 0, "time": time()}
        else:
            if time() - users[ip]["time"] > proxyConfig["config"]["proxy"]["requestTime"]:
                users.pop(ip, None)
            else:
                if users[ip]["count"] >= proxyConfig["config"]["proxy"]["requestLimit"]:
                    if ip not in blacklisted:
                        blacklisted[ip] = time() + proxyConfig["config"]["blocking"]["blockTime"]
                    users[ip]["count"] = 1

                try:
                    users[ip]["count"] += 1
                except KeyError:
                    pass

        if ip in blacklisted:
            remainingTime = int(blacklisted[ip] - time())

            if remainingTime <= 0:
                del blacklisted[ip]
            else:
                Logging.requestLog([request.method, ip, id, 3, request.url.path, request.query_params])
                return JSONResponse(
                    content={
                        "success": False, 
                        "message": f"This IP is temporarily blacklisted from using this LegoProxy Server for {convertTime(remainingTime)}."
                    }, 
                    status_code=429
                )
    
    response = await callNext(request)
    return response

@app.get("/")
async def proxyHome(json: bool = False):
    if not json:
        return FileResponse("./core/site/index.html")
    else:
        return {"success": True, "message": "LegoProxy Online!"}
    
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("./core/site/favicon.png")

@app.websocket("/relay")
async def relayServer(websocket: WebSocket):
    await websocket.accept()

    relayId = await websocket.receive_text()
    relay["connections"][relayId] = websocket
    Logging.proxyLog(f"Relay Client ({relayId}) is connecting to the Relay Server...")


    if env("RelayPassword") != "":
        Logging.proxyLog(f"Waiting for Password response to Relay Client ({relayId})...")
        await websocket.send_text("true")
        password = await websocket.receive_text()

        if password == env("RelayPassword"):
            Logging.proxyLog(f"Relay Client ({relayId}) has returned the correct Relay Password!")
            await websocket.send_text("authenticated")
        else:
            Logging.proxyLog(f"Relay Client ({relayId}) has returned the incorrect Relay Password. Disconnecting...")
            await websocket.send_text("notauthenticated")
            return await websocket.close()
    else:
        await websocket.send_text("false")


    Logging.proxyLog(f"Relay Client ({relayId}) has connected to the Relay Server!")

    if config()["relay_config"]["use_relay"]:
        await websocket.send_text("true")
    else:
        await websocket.send_text("false")


    try:
        while True:
            data = await websocket.receive_json()
            Logging.proxyLog(f"Receiving Data from Relay Client ({relayId})...")
            relay["responses"][data["id"]] = {}
            relay["responses"][data["id"]] = data["response"]
            Logging.proxyLog(f"Data Received from Relay Client ({relayId})!")

    except WebSocketDisconnect:
        del relay["connections"][relayId]
        Logging.proxyLog(f"Relay Client ({relayId}) has disconnected from the Relay Server.")
        await websocket.close()

# Added to differentiate responses from the host machine and relay clients.
@app.get("/relay/response/{id}")
async def relayResponse(id: str):
    try:
        response = relay["responses"][id]
        del relay["responses"][id]
    except KeyError:
        response = {"success": False, "message": f"No Relay Client response found for Response ID {id}."}
    return response

async def relayRequest(type: str, id: str, data: dict = {}):
    if not relay["connections"]:
        return "There are no Relay Clients connected to this LegoProxy Server."

    relayClient = choice(list(relay["connections"].keys()))
    await relay["connections"][relayClient].send_text(f"{type} {id}")
    await relay["connections"][relayClient].send_json(data)

    while id not in relay.get("responses", {}): 
        await asyncsleep(.000000001) # quick sleep
    
    # used to return the response directly back to host.
    # commented out since i wanna make relay responses different than host responses.
    #response = relay["responses"][id]
    #del relay["responses"][id]
    #return response
    
    return id

@app.get("/stats")
async def serverStats():
    total = sum(responseTime)
    try:
        average = total / len(responseTime)
    except ZeroDivisionError:
        average = 0
    
    return {
        "requests": config()["analytics"]["requests"],
        "averageProcTime": round(average * 1000),
        "lastProcTime": round(responseTime[len(responseTime)-1] * 1000),
        "relays": len(relay["connections"]),
        "relayEnabled": config()["relay_config"]["use_relay"]
    }


#@app.get("/{subdomain}/{path:path}")
#@app.post("/{subdomain}/{path:path}")
@app.get("/{subdomain}.roblox.com/{path:path}")
@app.post("/{subdomain}.roblox.com/{path:path}")
async def requestProxy(request: Request, subdomain: str, path: str, data: dict = Body({})):
    startTime = time()
    proxyConfig = config()
    subdomain = subdomain.lower()
    ip, id = request.headers.get("X-Forwarded-For"), request.headers.get("Roblox-Id")

    cacheKey = f"{ip}:{id}:{subdomain}.roblox.com/{path}?{request.query_params}"
    cachedResponse = cache.get(cacheKey)

    proxyConfig["analytics"]["requests"][0] += 1

    if cachedResponse and config()["config"]["proxy"]["cacheTTL"] != 0:
        endTime = time()
        responseTime.append(endTime - startTime)
        proxyConfig["analytics"]["requests"][2] += 1

        with open("./core/config.json", "w+") as file:
            dump(proxyConfig, file, indent=4)

        if not cachedResponse.get("success"):
            proxyConfig["analytics"]["requests"][1] += 1

        Logging.requestLog([request.method, ip, id, 1, request.url.path, request.query_params])
        return cachedResponse
    
    password = request.headers.get("ProxyPassword")

    if subdomain in proxyConfig["config"]["blocking"]["subdomains"]:
        Logging.requestLog([request.method, ip, id, 2, request.url.path, request.query_params])
        proxyConfig["analytics"]["requests"][1] += 1
        with open("./core/config.json", "w+") as file: dump(proxyConfig, file, indent=4)
        
        return {
            "success": False,
            "message": f"The Roblox API {subdomain}.roblox.com is being blocked by this LegoProxy Server."
        }

    if proxyConfig["config"]["proxy"]["placeId"] != 0 and id != proxyConfig["config"]["proxy"]["placeId"]:
        Logging.requestLog([request.method, ip, id, 2, request.url.path, request.query_params])
        proxyConfig["analytics"]["requests"][1] += 1
        gameId = proxyConfig["config"]["proxy"]["placeId"]
        with open("./core/config.json", "w+") as file: dump(proxyConfig, file, indent=4)

        return {
            "success": False,
            "message": f"This LegoProxy Server is only accepting requests from the following Game ID: {gameId}"
        }

    if env("ProxyPassword") != "" and password != env("ProxyPassword"):
        Logging.requestLog([request.method, ip, id, 2, request.url.path, request.query_params])
        proxyConfig["analytics"]["requests"][1] += 1
        with open("./core/config.json", "w+") as file: dump(proxyConfig, file, indent=4)

        return {
            "success": False,
            "message": "The ProxyPassword is incorrect."
        }
    
    try:
        if proxyConfig["relay_config"]["use_relay"] == True and relay["connections"]:
            jsonData = {
                "method": request.method,
                "subdomain": subdomain,
                "path": path,
                "query": f"{request.query_params}",
                "data": data
            }
            response = await relayRequest("HTTP", ShortUUID().random(12), jsonData)

            endTime = time()
            responseTime.append(endTime - startTime)
            if len(responseTime) > sets: responseTime.pop(0)
            return RedirectResponse(f"/relay/response/{response}")

        else:
            async with AsyncClient() as cli:
                if request.query_params == None:
                    req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}", json=data)
                else:
                    req = cli.build_request(request.method, f"https://{subdomain}.roblox.com/{path}?{request.query_params}", json=data)

                res = await cli.send(req)
                response = res.json()

    except JSONDecodeError: 
        Logging.requestLog([request.method, ip, id, 2, request.url.path, request.query_params])
        response = {
            "success": False,
            "message": f"The LegoProxy Server did not get a JSON Response from {subdomain}.roblox.com"
        }
        proxyConfig["analytics"]["requests"][1] += 1

    except ConnectError: 
        Logging.requestLog([request.method, ip, id, 2, request.url.path, request.query_params])
        response = {
            "success": False,
            "message": f"The LegoProxy Server could not connect to {subdomain}.roblox.com"
        }
        proxyConfig["analytics"]["requests"][1] += 1

    except RequestError:
        Logging.requestLog([request.method, ip, id, 2, request.url.path, request.query_params])
        response = {
            "success": False,
            "message": f"The LegoProxy Server could not send a request to {subdomain}.roblox.com"
        }
        proxyConfig["analytics"]["requests"][1] += 1

    endTime = time()
    responseTime.append(endTime - startTime)

    with open("./core/config.json", "w+") as file: dump(proxyConfig, file, indent=4)

    if len(responseTime) > sets: responseTime.pop(0)
    
    if config()["config"]["proxy"]["cacheTTL"] != 0: cache[cacheKey] = response
    Logging.requestLog([request.method, ip, id, 1, request.url.path, request.query_params])
    return response

@app.post("/webhook")
async def requestProxy(data: dict = Body({})):
    try:
        post(data["webhook"], json=data["data"])

    except ConnectError: 
        return {
            "success": False,
            "message": "The Webhook URL does not exist."
        }
            
    except RequestError:
        return {
            "success": False,
            "message": "Failed to send a Request to the Discord API."
        }

    except KeyError:
        return {
            "success": False,
            "message": "Data is missing from the POST Body. Do you have webhook and data inside?"
        }

    return {"success": True, "message": "Webhook Data has been sent Successfully!"}

@app.exception_handler(404)
async def nf404handler(request: Request, a):
    ip, id = request.headers.get("X-Forwarded-For"), request.headers.get("Roblox-Id")
    Logging.requestLog([request.method, ip, id, 3, request.url.path, request.query_params])
    return JSONResponse(
        content={
            "success": False,
            "message": "LegoProxy Route not Found."
        },
        status_code=404
    )

def cleanup():
    while True:
        for proxyIp, data in list(users.items()):
            if time() - data["time"] > config()["config"]["proxy"]["requestTime"]:
                del users[proxyIp]

        sleep(1)

@app.on_event("startup")
async def userCleanup():
    t = Thread(target=cleanup)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    Logging.proxyLog("LegoProxy Started!")
    run("main:app", host="0.0.0.0", port=443, reload=True, log_level="warning")
