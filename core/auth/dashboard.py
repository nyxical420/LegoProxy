from core.conf import LegoProxyConfig

config = LegoProxyConfig()

def validate_credentials(username: str, password: str):
    if username != config.dashboardUsername: return False
    if password != config.dashboardPassword: return False
    return True