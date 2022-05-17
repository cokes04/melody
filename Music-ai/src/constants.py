import os
from pathlib import Path
import math

EMOTIONS = ["delighted", "enthusiastic", "gloomy", "mysterious", "relaxed", "tense"]

NUM_NOTES = 2150   #2150 #9153
NUM_DURATION = 124 #124 #109

NUM_EMOTION = 6

SEQ_LEN = 128

MUSIC_AI_DIR = Path(os.path.abspath(__file__)).parent.parent

DATA_DIR =  os.path.join(MUSIC_AI_DIR, "data")
DATASET_DIR = os.path.join(MUSIC_AI_DIR, "dataset")

MODEL_DIR =  os.path.join(MUSIC_AI_DIR, "models")
MODEL_NAME = "model.h5"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

OUTPUT_DIR = os.path.join(MUSIC_AI_DIR, "generate")