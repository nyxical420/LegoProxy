from colorama import Fore, init
init(autoreset=True)

def log(method, ip, status: int, path: str, query: str):
    color = {0: Fore.LIGHTBLUE_EX, 1: Fore.LIGHTGREEN_EX, 2: Fore.LIGHTYELLOW_EX, 3: Fore.LIGHTRED_EX}
    icon = {0: "-->", 1: "<--", 2: "-!-", 3: "-X-"}
    url = path
    
    if query != None: url += f"?{query}"

    print(color[status] + f"[ LP - {method} ]    {ip} {icon[status]} {url}")