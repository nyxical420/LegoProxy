# SimpleLegoProxy
SimpleLegoProxy is a VERY simple Roblox Proxy by accessing Roblox Resources through HTTPService.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/Nod3IF?referralCode=pmHjGZ)

## SimpleLegoProxy Usage
SimpleLegoProxy is very easy to use. It works by querying an Roblox API Subdomain and Providing the path for your request.

For example, you want to get a user's information. you would normally request:
```
https://users.roblox.com/v1/users/1
```

But with SimpleLegoProxy, you will request:
```
https://proxy.veriblox.ml/users?path=v1/users/1
```

## SimpleLegoProxy Rotation
To rotate your proxy to new IPs per request. you can provide SimpleLegoProxy the IPs inside a text file (`proxies.txt`).\
To do a request in a rotating IP, you can add `/rotate` in your URL path.
```
https://proxy.veriblox.ml/rotate/users?path=v1/users/1
```

## SimpleLegoProxy Self-Hosting
You can host SimpleLegoProxy by yourself by downloading the source code and running it to your server if you are having issues getting the json response your expecting.\
However, if you don't own a VPS. you can always use free hosting sites like Replit or Railway.

The performance of the two mentioned hosting services may not be fast. but its better than not being able to own a VPS which you need to pay monthly.

To deploy SimpleLegoProxy to Railway, you can click the button above the README or by [clicking this](https://railway.app/new/template/Nod3IF?referralCode=pmHjGZ).

To deploy SimpleLegoProxy to Replit, You can download the source code to your computer and uploading all of it inside your repl. after that, you will need to use UptimeRobot to keep your repl online to avoid it from sleeping.
