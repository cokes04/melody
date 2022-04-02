import os
import datetime as dt
from tensorflow.keras import models
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation, Concatenate, Input, Reshape, Embedding, Bidirectional, LeakyReLU, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import plot_model
import tensorflow as tf
import numpy as  np

model_dir = 'models'
model_name = 'LSTM'

def create_model(seq_shape) :

    model = Sequential()
    model.add(LSTM(256, input_shape=seq_shape, return_sequences=True))
    model.add(Bidirectional(LSTM(256)))
    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(1024))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(np.prod(seq_shape), activation='tanh'))
    model.add(Reshape(seq_shape))
    model.summary()
    plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)

    seq = Input(shape=seq_shape)
    validity = model(seq)

    return Model(seq, validity)

def load_last_model() :
    file_list = os.listdir(model_dir)

    if len(file_list) == 0 :
        raise Exception('Failed Load Last Model : None of the models exist')

    file_list.sort(reverse=True)

    return load_model(file_list[0])

def load_model(name : str) :
    model = models.load_model(f'{model_dir}/{name}')
    print("Load Model : ", name)

    model.summary()

    return model

def save_model(model) :
    os.makedirs(model_dir, exist_ok=True)

    now = dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')

    file_path = f'{model_dir}/{model_name}-{now}.h5'
    model.save(file_path)
    print("Save Model : ", file_path)

def train(model, train_x, train_y) :
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

    history = model.fit(train_x, train_y, epochs=50, batch_size=64, callbacks=callbacks_list)
    return history