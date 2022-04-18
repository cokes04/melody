import os
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation, Input, TimeDistributed, Conv1D
from tensorflow.keras.layers import Concatenate, RepeatVector, Add, Lambda, Permute, Reshape
from tensorflow.keras import losses
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as  np

from dataset import *
from constants import  *


def build_models(time_steps=IN_SEQ_LEN, input_dropout=0.2, dropout=0.5):
    print("Build Models")

    notes_in = Input(shape=(time_steps, NUM_NOTES, 1) )
    time_in = Input( shape=(time_steps) )
    emotion_in = Input( shape=(NUM_EMOTION) )
    chosen_in = Input((time_steps, NUM_NOTES, NOTE_UNITS))


    notes = Dropout(input_dropout)(notes_in)
    time = Dropout(input_dropout)(time_in)
    chosen = Dropout(input_dropout)(chosen_in)

    emotion_l = Dense(EMOTION_UNITS, name='emotion')
    emotion = emotion_l(emotion_in)

    time_out = time_axis(dropout)(notes, time, emotion)

    naxis = note_axis(dropout)
    notes_out = naxis(time_out, chosen, emotion)

    model = Model([notes_in, time_in, emotion_in], [notes_out])
    model.compile(optimizer='nadam', loss=[primary_loss])


    time_model = Model([notes_in, time_in, emotion_in], [time_out])


    note_features = Input((1, NUM_NOTES, TIME_AXIS_UNITS), name='note_features')
    chosen_gen_in = Input((1, NUM_NOTES, NOTE_UNITS), name='chosen_gen_in')
    enotion_gen_in = Input((1, NUM_EMOTION), name='emotion_in')


    chosen_gen = Dropout(input_dropout)(chosen_gen_in)
    enotion_gen = emotion_l(enotion_gen_in)

    note_gen_out = naxis(note_features, chosen_gen, enotion_gen)

    note_model = Model([note_features, enotion_gen_in], note_gen_out)

    return model, time_model, note_model

def load_models(name = MODEL_NAME):
    models = build_models()
    models[0].summary()
    try:
        models[0].load_weights(f'{MODEL_DIR}/{name}')
        print('Loaded model from file.')
    except:
        print('Unable to load model from file.')
    return models


if __name__=="__main__" :
    print("Model Main")
    build_models()