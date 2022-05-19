import os
class Config(object):
    WEB_PASSWORD = os.getenv("FW_WEB_PASSWORD", "password")
    API_TOKEN = os.getenv("FW_API_TOKEN", "token")

    TEAM_ID = os.getenv("FW_TEAM_ID", "27")
    VM_SUBNET = os.getenv("FW_VM_SUBNET", "60")
    YOUR_TEAM = f"10.{VM_SUBNET}.{TEAM_ID}.1"
    TEAM_TOKEN = os.getenv("FW_TEAM_TOKEN", "8a8d25f465bec01d")
    TEAMS = ["127.0.0.1"]
    # TEAMS.remove(YOUR_TEAM)

    ROUND_DURATION = int(os.getenv("FW_ROUND_DURATION", 120))
    FLAG_ALIVE = 5 * ROUND_DURATION
    FLAG_FORMAT = r"[A-Z0-9]{31}="

    SUB_LIMIT = int(os.getenv("FW_SUB_LIMIT", 1))
    SUB_INTERVAL = int(os.getenv("FW_SUB_INTERVAL", 5))
    SUB_PAYLOAD_SIZE = int(os.getenv("FW_SUB_PAYLOAD_SIZE", 100))
    SUB_HOST = os.getenv("FW_SUB_HOST", "10.1.0.2")
    SUB_PORT = int(os.getenv("FW_SUB_PORT", "80"))
    SUB_ENDPOINT = os.getenv("FW_SUB_ENDPOINT", "/flags")
    SUB_USE_HTTP = True if os.getenv("FW_SUB_USE_HTTP", "True") == "True" else False
    SUB_URL = f"http://{SUB_HOST}:{SUB_PORT}{SUB_ENDPOINT}"

    SUB_ACCEPTED = os.getenv("FW_SUB_ACCEPTED", "accepted")
    SUB_INVALID = os.getenv("FW_SUB_INVALID", "invalid")
    SUB_OLD = os.getenv("FW_SUB_OLD", "too old")
    SUB_YOUR_OWN = os.getenv("FW_SUB_YOUR_OWN", "your own")
    SUB_STOLEN = os.getenv("FW_SUB_STOLEN", "already stolen")
    SUB_NOP = os.getenv("FW_SUB_NOP", "from NOP team")
    SUB_NOT_AVAILABLE = os.getenv("FW_SUB_NOT_AVAILABLE", "is not available")

    DB_NSUB = os.getenv("FW_DB_NSUB", "NOT_SUBMITTED")
    DB_SUB = os.getenv("FW_DB_SUB", "SUBMITTED")
    DB_SUCC = os.getenv("FW_DB_SUCC", "SUCCESS")
    DB_ERR = os.getenv("FW_DB_ERR", "ERROR")
    DB_EXP = os.getenv("FW_DB_EXP", "EXPIRED")

    SECRET_KEY = os.getenv("FW_SECRET_KEY", "changeme")

    DATABASE = os.getenv("FW_DATABASE", "instance/flagWarehouse.sqlite")
