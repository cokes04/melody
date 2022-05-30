from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import LSTM, Dense, Activation, Input, Embedding
from tensorflow.python.keras.layers import Concatenate, RepeatVector, Lambda, Permute, Reshape, Multiply
import tensorflow.python.keras.backend as K
from tensorflow.python.keras.optimizers import adam_v2
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

    opti = adam_v2.Adam(learning_rate=0.003, )
    model.compile(loss=['categorical_crossentropy', 'categorical_crossentropy'], optimizer=opti, metrics='accuracy')

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