import os
from tensorflow.keras import models
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation, Bidirectional, LeakyReLU
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import plot_model
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as  np
from dataset import *

from constants import  *

def build_model(seq_shape, n_vocab) :
    logging.info("Create Model")

    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=seq_shape,
        return_sequences=True
    ))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(512))
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)
    return model

def load_model(name = MODEL_NAME) :
    print(f"Load Model: {name}")
    model = models.load_model(f'{MODEL_DIR}/{name}')

    return model

def save_model(model, name = MODEL_NAME) :
    print(f"Save Model: {MODEL_DIR}")

    os.makedirs(MODEL_DIR, exist_ok=True)

    file_path = f'{MODEL_DIR}/{name}'
    model.save(file_path)

if __name__ == '__main__':
    model = build_model()
    save_model(model)