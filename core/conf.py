class LegoProxyConfig():
    proxyAuthKey: str = None
    maxRequests: int = None
    webhookUrl: str = None
    placeId: int = None
    rotate: bool = False

    blacklistedSubdomains: list = ["servers"]

    dashboardEnabled: bool = False

    # Username and Password must be lowercase.
    dashboardUsername: str = None
    dashboardPassword: str = None