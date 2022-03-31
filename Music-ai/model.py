import os
import datetime as dt
from tensorflow.keras import models
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation
from tensorflow.keras.callbacks import ModelCheckpoint
import tensorflow as tf


model_dir = 'models'
model_name = 'LSTM'

def create_model(window_size, n_vocab) :

    model = Sequential()
    model.add(LSTM(
        256,
        input_shape=(window_size, 1),
        return_sequences=True
    ))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(256))
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])
    model.summary()

    return model

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

    file_path = f'{model_dir}/{model_name}_{now}.h5'
    model.save(file_path)
    print("Save Model : ", file_path)

def train(model, train_input, train_output) :
    filepath = "models/LSTM-weights-{epoch:02d}-{loss:.4f}.h5"
    checkpoint = ModelCheckpoint(
        filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    history = model.fit(train_input, train_output, epochs=50, batch_size=64, callbacks=callbacks_list)
    return history