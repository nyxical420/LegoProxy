class LegoProxyConfig():
    proxyAuthKey: str = None
    maxRequests: int = None
    webhookUrl: str = None
    placeId: int = None
    rotate: bool = False

    blacklistedSubdomains: list = []

    dashboardEnabled: bool = False
    dashboardUsername: str = None
    dashboardPassword: str = None