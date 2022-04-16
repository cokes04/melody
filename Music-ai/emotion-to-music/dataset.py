import os
import csv
import pickle
import glob
import logging
import numpy as np
from music21 import *
import tensorflow.keras.utils as np_utils

from constants import *

def get_files(path):
    potential_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            fname = os.path.join(root, f)
            if os.path.isfile(fname) and fname.endswith('.mid'):
                potential_files.append(fname)
    return potential_files

def create_dataset() :
    print("Create Dataset")

    for i, emotion in enumerate(EMOTIONS) :
        path = f"{DATA_DIR}/{emotion}"
        fnames = get_files(path)


def load_dataset() :
    return None

if __name__ == '__main__':
    print("Dataset Main")
    create_dataset()