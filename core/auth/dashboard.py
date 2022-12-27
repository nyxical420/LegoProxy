from core.conf import LegoProxyConfig

def validate_credentials(username: str, password: str, config: LegoProxyConfig):
    if username != config.dashboardUsername: return False
    if password != config.dashboardPassword: return False
    return True