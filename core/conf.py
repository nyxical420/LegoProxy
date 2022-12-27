class LegoProxyConfig():
    proxyAuthKey: str = None
    maxRequests: int = None
    webhookUrl: str = None
    placeId: int = None
    rotate: bool = False

    blacklistedSubdomains: list[str] = ["servers"]
    blacklistedGameIds: list[int] = []

    dashboardEnabled: bool = False

    # Username and Password must be lowercase.
    dashboardUsername: str = "admin"
    dashboardPassword: str = None