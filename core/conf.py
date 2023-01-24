class LegoProxyConfig():
    proxyAuthKey: str = ""
    maxRequests: int = 0
    placeId: int = 0
    caching: bool = True
    expiry: int = 0

    blacklistedSubdomains: list = []

    dashboardUsername: str = None
    dashboardPassword: str = None