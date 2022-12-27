from json import loads
from asyncio import sleep
from httpx import AsyncClient
from json.decoder import JSONDecodeError
from random import choice, randint, random
from httpx._exceptions import ConnectError, ConnectTimeout

from core.conf import LegoProxyConfig
proxylist = open("proxies.txt", "r").read().split()

async def logRequest(method, subdomain, path, response, useragent, id, config: LegoProxyConfig):
    requestId = ""
    for i in range(7): requestId += chr(randint(ord('a'), ord('z'))) if random() < 0.5 else str(randint(0, 9))

    data = {"content":None,"embeds":[{"title":f"LegoProxy Request Logs ({method}, {id}, {requestId})","color":3092790,"fields":[{"name":"Request Endpoint","value":f"**{subdomain}**.roblox.com","inline":True},{"name":"Request Path","value":f"[/{path}](https://users.roblox.com/{path})","inline":True},{"name":"Data Response","value":f"```json\n{response}\n```"}, {"name":"Request User-Agent","value":f"**{useragent}**"}]}],"username":"LegoProxy","avatar_url":"https://cdn.discordapp.com/attachments/1056074242325741578/1056074861690224720/legoproxy.png","attachments":[]}
    proxyRequest.log = f"[{method} ({id}, {requestId})] LegoProxy --> {subdomain}.roblox.com/{path}\nResponse:\n{response}\nUser-Agent: {useragent}\n"

    if config.webhookUrl == "": return
    async with AsyncClient() as cli:
        await cli.post(config.webhookUrl, json=data)

async def resetRequestsCounter():
    while True:
        await sleep(1)
        proxyRequest.totalRequests -= proxyRequest.totalRequests


class proxyRequest():
    log = ""
    
    totalRequests = 0
    subdomain: str
    path: str
    data: str
    method: str
    rotate: bool

    authRobloxId: int
    authKey: str

    authUserAgent: str

    async def request(self, config: LegoProxyConfig):
        if self.subdomain in config.blacklistedSubdomains:
            return {"success": False, "message": "LegoProxy - The Roblox API Subdomain is Blacklisted to this LegoProxy server."}

        if self.totalRequests > config.maxRequests:
            return {"success": False, "message": "LegoProxy - Requests Overload. Please try again!"}

        if config.placeId != None: 
            if self.authRobloxId != config.placeId:
                if self.authRobloxId != config.blacklistedGameIds:
                    return {"success": False, "message": "LegoProxy - This proxy is only accepting requests from a Roblox Game."}

        if config.proxyAuthKey != None:
            if self.authKey != config.proxyAuthKey:
                return {"success": False, "message": "LegoProxy - This proxy requires an Authentication Key."}

        try:
            if self.rotate:
                proxy = choice(proxylist)
                async with AsyncClient(proxies={"http://": f"http://{proxy}"}) as cli:
                    if self.method == "GET":
                        response = await cli.get(f"https://{self.subdomain}.roblox.com/{self.path}")
                    if self.method == "POST":
                        response = await cli.post(f"https://{self.subdomain}.roblox.com/{self.path}", data=loads(self.data))
                    if self.method == "PATCH":
                        response = await cli.patch(f"https://{self.subdomain}.roblox.com/{self.path}", data=loads(self.data))
                    if self.method == "DELETE":
                        response = await cli.delete(f"https://{self.subdomain}.roblox.com/{self.path}", data=loads(self.data))
                    
                    response = response.json()
            
            if not self.rotate:
                async with AsyncClient() as cli:
                    if self.method == "GET":
                        response = await cli.get(f"https://{self.subdomain}.roblox.com/{self.path}").json()
                    if self.method == "POST":
                        response = await cli.post(f"https://{self.subdomain}.roblox.com/{self.path}", data=loads(self.data)).json()
                    if self.method == "PATCH":
                        response = await cli.patch(f"https://{self.subdomain}.roblox.com/{self.path}", data=loads(self.data)).json()
                    if self.method == "DELETE":
                        response = await cli.delete(f"https://{self.subdomain}.roblox.com/{self.path}", data=loads(self.data)).json()

                    response = response.json()

        except JSONDecodeError: 
            response = {"success": False, "message": "LegoProxy - Roblox API did not return JSON Data."}

        except ConnectTimeout: 
            if not self.rotate: response = {"success": False, "message": "LegoProxy - Request Timed Out."}
            if self.rotate: response = {"success": False, "message": f"LegoProxy - Request Timed Out. Proxy IP: {proxy}"}

        except ConnectError: 
            response = {"success": False, "message": "LegoProxy - Roblox API Subdomain does not exist."}

        self.totalRequests += 1
        await logRequest(self.method, self.subdomain, self.path, response, self.authUserAgent, config.placeId, config)
        return response