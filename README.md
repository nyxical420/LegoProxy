# LegoProxy
LegoProxy - A rotating Roblox Proxy for accessing Roblox APIs through HTTPService

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/Nod3IF?referralCode=pmHjGZ)

## Note
Please do not use somebody else's LegoProxy server unless you trust them. They can easily fake your requests to send forged or fake data to your game and possibly break it. It is recommended you host your own LegoProxy server to prevent recieving forged or fake data.

## LegoProxy Usage
LegoProxy is very easy to use. It works by querying an Roblox API Subdomain and Providing the path for your request.

For example, you want to get a user's information. you would normally request:
```
https://users.roblox.com/v1/users/1
```

But with LegoProxy, you will request:
```
https://legoproxy.deta.dev/users?e=v1/users/1
```

## LegoProxy IP Rotation
To rotate your proxy to new IPs per request. you can provide LegoProxy the IPs inside a text file (`proxies.txt`).\
To do a request in a rotating IP, you can add `/rotate` in your URL path.
```
https://legoproxy.deta.dev/rotate/users?e=v1/users/1
```

## LegoProxy Self-Hosting
redoing
