# LegoProxy
LegoProxy - A rotating Roblox Proxy for accessing Roblox APIs through HTTPService

## Note
1. Please do not use somebody else's LegoProxy server unless you trust them. They can easily fake your requests to send forged or fake data to your game and possibly break it. It is recommended you host your own LegoProxy server to prevent recieving forged or fake data.

2. This does not show any HTML. It only accepts recieving JSON Data from the API and Endpoint you are requesting on and return the data to you.

## LegoProxy Usage
LegoProxy is very easy to use. It works by querying an Roblox API Subdomain and Providing the path for your request.

For example, you want to get a user's information. you would normally request:
```
https://users.roblox.com/v1/users/1
```

But with LegoProxy, you will request:
```
https://legoproxy.deta.dev/users/v1/users/1
```

## LegoProxy IP Rotation
To rotate your proxy to new IPs per request. you can provide LegoProxy the IPs inside a text file (`proxies.txt`).\
To do a request in a rotating IP, you can add `/rotate` in your URL path.
```
https://legoproxy.deta.dev/rotate/users/v1/users/1
```

## LegoProxy GameLock
To lock LegoProxy to your game only, you can set the `placeId` value in the code to your Roblox Game Id to prevent unwanted request coming outside from your game.\
**NOTE:** This prevents you from being able to access your Proxy in your browser.

## LegoProxy Self-Hosting
You can host LegoProxy on Paid or Free Services.

But for this one, we will be focusing on hosting LegoProxy inside a Free Host, [Deta](https://www.deta.sh/) or [Deta Space](https://alpha.deta.space/).

