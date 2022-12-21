# LegoProxy
LegoProxy - A rotating Roblox Proxy for accessing Roblox APIs

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/Nod3IF?referralCode=pmHjGZ)

## Note
Please do not use somebody else's LegoProxy server unless you trust them. They can easily fake your requests to send forge / fake data to your game and possibly break it. It is recommended you host your own LegoProxy server to prevent forged data.

## LegoProxy Usage
LegoProxy is very easy to use. It works by querying an Roblox API Subdomain and Providing the path for your request.

For example, you want to get a user's information. you would normally request:
```
https://users.roblox.com/v1/users/1
```

But with LegoProxy, you will request:
```
https://proxy.veriblox.ml/users?e=v1/users/1
```

## LegoProxy IP Rotation
To rotate your proxy to new IPs per request. you can provide LegoProxy the IPs inside a text file (`proxies.txt`).\
To do a request in a rotating IP, you can add `/rotate` in your URL path.
```
https://proxy.veriblox.ml/rotate/users?e=v1/users/1
```

## LegoProxy Self-Hosting
You can host LegoProxy by yourself by downloading the source code and running it to your server if you are having issues getting the json response your expecting.\
However, if you don't own a VPS. you can always use free hosting sites like Replit or Railway.

The performance of the two mentioned hosting services may not be fast. but its better than not being able to own a VPS which you need to pay monthly.

To deploy LegoProxy to Railway, you can click the button above the README or by [clicking this](https://railway.app/new/template/Nod3IF?referralCode=pmHjGZ).

To deploy LegoProxy to Replit, You can download the source code to your computer and uploading all of it inside your repl. after that, you will need to use UptimeRobot to keep your repl online to avoid it from sleeping.
