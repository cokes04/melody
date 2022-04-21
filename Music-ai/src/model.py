from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation, Input, Embedding
from tensorflow.keras.layers import Concatenate, RepeatVector, Lambda, Permute, Reshape, Multiply
import tensorflow.keras.backend as K
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.utils import plot_model
import tensorflow as tf
from constants import *

def build_models(time_steps = SEQ_LEN, embed_size = 100, rnn_units=256):
    note_in = Input(shape=(None,), name="note_in")
    duration_in  = Input(shape=(None,), name="duration_in")

    x1 = Embedding(NUM_NOTES, embed_size)(note_in)
    x2 = Embedding(NUM_DURATION, embed_size)(duration_in)

    x = Concatenate()([x1, x2])
    x = LSTM(rnn_units, return_sequences=True)(x)
    x = LSTM(rnn_units, return_sequences=True)(x)
    e = Dense(1, activation='tanh')(x)
    e = Reshape([-1])(e)
    alpha = Activation('softmax')(e)
    alpha_repeated = Permute([2, 1])(RepeatVector(rnn_units)(alpha))

    c = Multiply()([x, alpha_repeated])
    l = Lambda(lambda xin: K.sum(xin, axis=1), output_shape=(rnn_units,))
    c = l(c)

    note_out = Dense(NUM_NOTES, activation='softmax', name='pitch')(c)
    duration_out = Dense(NUM_DURATION, activation='softmax', name='duration')(c)

    att_model = Model([note_in, duration_in], alpha)
    model = Model([note_in, duration_in], [note_out, duration_out])

    opti = SGD(learning_rate=0.003, )
    model.compile(loss=['categorical_crossentropy', 'categorical_crossentropy'], optimizer=opti, metrics='accuracy')

    plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)
    return model, att_model

def load_models(path = MODEL_PATH):
    model, att_model = build_models()

    try:
        model.load_weights(path)
        print('Loaded Model File')
    except:
        print('Unloaded Model File.')

    model.summary()
    return model, att_model


if __name__=="__main__" :
    print("Model Main")
    build_models()
