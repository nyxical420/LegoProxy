# LegoProxy
A rotating Roblox Proxy for accessing Roblox APIs through HTTPService

## Deploy LegoProxy
More Deploy buttons will be added when i find a free hosting service that can host proxies like this.

[![Deploy](https://button.deta.dev/1/svg)](https://go.deta.dev/deploy?repo=https://github.com/PyTsun/LegoProxy)

## LegoProxy Usage
For example, we want to get Roblox's Roblox Information by his Roblox ID.

From the Roblox API, you would normally create a GET Request from the URL:
```
https://users.roblox.com/v1/users/1
```

But with LegoProxy, You will have to place the Endpoint from the URL path before the API path you want to create a GET Request from:
```
https://legoproxy.deta.dev/users/v1/users/1
```

Requesting to LegoProxy follows the following format:
```
https://legoproxy.deta.dev/<subdomain>/<path>
```

Requesting to LegoProxy follows the following format if you are going to request with a Rotating IP:
```
https://legoproxy.deta.dev/rotate/<subdomain>/<path>
```

## LegoProxy Features
- Access to all Roblox APIs and Endpoints
- Ability to Rotate to different IPs
- Accept Request only coming from your Roblox Game by Id
- Verify Requests that is coming from you by an Authentication Key (a.k.a Password)

## LegoProxy Disclaimer
It is highly recommended to host LegoProxy by yourself if you are going to use it for Production Applications or Roblox Games. as you may be getting Fake or Forged data and slowdowns that could do damage to your Production Applocations or Roblox Games.

## LegoProxy Self-Hosting
You can host LegoProxy by your own by deploying LegoProxy to one of [these](https://github.com/PyTsun/LegoProxy/blob/main/README.md#deploy-legoproxy) free hosting services.
If you own a VPS, you can install the following packages inside a venv and run it by `python3 start.py` or `uvicorn main:app --host 0.0.0.0 --port 443`.
