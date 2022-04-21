import os
from pathlib import Path
import math
EMOTIONS = [ "delighted", "gloomy", "relaxed", "tense"]

#included_etc   #excluded_etc
#13523  #73     #17848  #220
#included_etc_chordify  #excluded_etc_chordify
#123966  #141           #106826  #141
#excluded_etc_chordify_half    #excluded_etc_chordify_third    #excluded_etc_chordify_quarter
#57500   #137                   39556  #131                     #29654  #123
#excluded_etc_chordify_third_slice_four     #excluded_etc_chordify_quarter_slice_four   #excluded_etc_chordify_fifth_slice_four
#23677  #131                                #19364   #123                               #16862  #117
#excluded_etc_chordify_sixth_slice_four
#14783  #114

NUM_NOTES = 14782
NUM_DURATION = 114

NUM_EMOTION = 4

SEQ_LEN = 128

MUSIC_AI_DIR = Path(os.path.abspath(__file__)).parent.parent

DATA_DIR =  os.path.join(MUSIC_AI_DIR, "data")
NEW_DATA_DIR =  os.path.join(DATA_DIR, "new")
DATASET_DIR = os.path.join(MUSIC_AI_DIR, "dataset")

MODEL_DIR =  os.path.join(MUSIC_AI_DIR, "models")
MODEL_NAME = "model.h5"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

OUTPUT_DAR = os.path.join(MUSIC_AI_DIR, "generate")
