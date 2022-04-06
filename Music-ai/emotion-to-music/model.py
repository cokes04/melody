import os
import logging
import datetime as dt
from tensorflow.keras import models
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation, Bidirectional, LeakyReLU
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import plot_model
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as  np
from preprocessing import *

logging.basicConfig(level=logging.INFO)
model_dir = './models'
model_name = 'LSTM'

#일단 복붙
def create_model(seq_shape, n_vocab) :
    logging.info("Create Model")

    model = Sequential()
    model.add(LSTM(256, input_shape=seq_shape, return_sequences=True))
    model.add(Bidirectional(LSTM(512)))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])
    model.summary()
    plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)

    return model

def load_last_model() :
    file_list = os.listdir(model_dir)

    if len(file_list) == 0 :
        raise Exception('Failed Load Last Model : None of the models exist')

    file_list.sort(reverse=True)

    return load_model(file_list[0])

def load_model(name : str) :
    model = models.load_model(f'{model_dir}/{name}')
    print(f"Load Model: {name}")

    model.summary()

    return model

def save_model(model) :
    os.makedirs(model_dir, exist_ok=True)

    now = dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')

    file_path = f'{model_dir}/{model_name}-{now}-0.h5'
    logging.info(f"Save Model: {file_path}")
    model.save(file_path)


def train(model, train_x, train_y) :
    logging.info("Model Train")

    now = dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')

    filepath = f"{model_dir}/{model_name}-{now}" + "-weights-{epoch:02d}-{loss:.4f}.h5"
    checkpoint = ModelCheckpoint(
        filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    history = model.fit(train_x, train_y, epochs=2, batch_size=64, callbacks=callbacks_list)
    return history


def show_train_result(history, is_save=True) :
    plt.plot(history.history['accuracy'])
    plt.title('Model accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend(['Train', 'Test'], loc='upper left')
    if is_save :
        now = dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        plt.savefig(f'train_result-{now}.png')

    plt.show()

if __name__ == '__main__':
    model = create_model(get_seq_shape(), get_n_vocab())
    save_model(model)