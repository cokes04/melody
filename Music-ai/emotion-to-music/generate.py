import numpy as np
from music21 import *
import os
import re
import random

from model import *
from constants import *

def generate(model, music_length, input_emotion) :
    print("Generate Music")

if __name__ == '__main__':
    model = load_model()
    music_length = 200
    emotion = 2

    generate(model, music_length, emotion)