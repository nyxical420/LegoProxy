import time
from asyncio import sleep
from json.decoder import JSONDecodeError

from httpx import AsyncClient
from httpx._exceptions import ConnectError, ConnectTimeout, RequestError

from core.conf import LegoProxyConfig

proxylist = open("proxies.txt", "r").read().split()

async def resetRequestsCounter():
    while True:
        await sleep(1)
        proxyRequest.totalRequests -= proxyRequest.totalRequests

class proxyRequest():
    log = ""
    
    totalRequests = 0
    subdomain: str
    path: str
    data: dict
    method: str

    authRobloxId: int
    authKey: str

    authUserAgent: str

    last_used_proxy = -1
    cache = {}
    cache_expiry_time = 1800

    async def request(self, config: LegoProxyConfig):
        cache_key = (self.subdomain, self.path, tuple(self.data.items()), self.method)
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if cache_entry["timestamp"] + self.cache_expiry_time > time.time():
                return cache_entry["response"]
            else:
                del self.cache[cache_key]

        if self.subdomain in config.blacklistedSubdomains:
            return {"success": False, "message": "LegoProxy - The Roblox API Subdomain is Blacklisted to this LegoProxy server."}

        if self.totalRequests > config.maxRequests:
            return {"success": False, "message": "LegoProxy - Requests Overload. Please try again!"}

        if config.placeId != None: 
            if self.authRobloxId != config.placeId:
                return {"success": False, "message": "LegoProxy - This proxy is only accepting requests from a Roblox Game."}

        if config.proxyAuthKey != None:
            if self.authKey != config.proxyAuthKey:
                return {"success": False, "message": "LegoProxy - This proxy requires an Authentication Key."}

        self.last_used_proxy = (self.last_used_proxy + 1) % len(proxylist)
        proxy = proxylist[self.last_used_proxy]

        try:
            async with AsyncClient(proxies={"http://": f"http://{proxy}"}, http2=True) as cli:
                req = cli.build_request(self.method, f"https://{self.subdomain}.roblox.com/{self.path}", data=self.data)
                res = await cli.send(req)
                response = res.json()     

        except JSONDecodeError: 
            response = {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}

        except ConnectTimeout: 
            response = {"success": False, "message": f"LegoProxy - Connection Timeout. Proxy IP {proxy} could be a dead proxy."}

        except ConnectError: 
            response = {"success": False, "message": "LegoProxy - Roblox API Subdomain does not exist."}
        
        except RequestError:
            response = {"success": False, "message": "LegoProxy - Failed to create a request."}

        self.totalRequests += 1

        self.cache[cache_key] = {
            "timestamp": time.time(),
            "response": response,
        }
        return response

