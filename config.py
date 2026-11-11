import os

from dotenv import load_dotenv

load_dotenv()

# App settings

APP_NAME = "GAIA - Sustainability Intelligence Platform"

APP_VERSION = "1.0"

# Model settings

TEXT_MODEL = "distilbert-base-uncased"

IMAGE_MODEL = "mobilenet_v3_small"

VOICE_MODEL = "tiny"  # Whisper tiny (39MB)

# Green AI settings

CARBON_INTENSITY = 400  # gCO2 per kWh (India average)

CPU_POWER_WATTS = 65

# Database

DATABASE_PATH = "data/gaia.db"

# Score thresholds

GAIA_THRESHOLDS = {

"excellent": 80,
"good": 60,
"poor": 40,
"critical": 20
}
