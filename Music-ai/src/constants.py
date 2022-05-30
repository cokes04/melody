import os
from pathlib import Path
EMOTIONS = ["delighted", "gloomy", "relaxed"]

NUM_NOTES = 2068   #2068 #9153
NUM_DURATION = 133  #133 #109

NUM_EMOTION = 3

SEQ_LEN = 128

BUCKET_NAME = "generate-music-registry-dev-078916624102"

S3_GENERATED_MUSIC_URL = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/generatedMusic"


SRC_DIR = Path(os.path.abspath(__file__)).parent
TMP_DIR = "/tmp"
GENERATE_DIR = os.path.join(TMP_DIR, "generate")

MODEL_NAME = "model.h5"
MODEL_PATH = os.path.join(TMP_DIR, MODEL_NAME)
