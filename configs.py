
from os import path, getenv

class Config:
    API_ID = int(getenv("API_ID", "29707147"))
    API_HASH = getenv("API_HASH", "ceff19669a8941be50f5c2b2fedd3b97")
    BOT_TOKEN = getenv("BOT_TOKEN", "7637892776:AAG6YX90hEazGQrYjlKSZe1q6pyqMzi-CY0")
    # Your Force Subscribe Channel Id Below 
    CHID = int(getenv("CHID", "-1002312364035")) # Make Bot Admin In This Channel

    SUDO = list(map(int, getenv("SUDO", "1095477203").split()))
    MONGO_URI = getenv("MONGO_URI", "mongodb+srv://ashrfalkhtry654:5WCV1Tul8zyneLUI@cluster0.6o90p.mongodb.net/auto_requestDB?retryWrites=true&w=majority&appName=Cluster0")
    
cfg = Config()

#mongodb+srv://ashrfalkhtry654:5WCV1Tul8zyneLUI@cluster0.6o90p.mongodb.net/auto_requestDB?retryWrites=true&w=majority&appName=Cluster0