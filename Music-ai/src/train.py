import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import tensorflow as tf
import os

from model import *
from dataset.load import *
from dataset.create import *

#os.environ["TF_GPU_ALLOCATOR"]='cuda_malloc_async'
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            gpus: tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        print(e)

    try:
        tf.config.experimental.set_virtual_device_configuration(
        gpus[0],
        [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=4096)])
    except RuntimeError as e:
        print(e)

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.99
session = tf.compat.v1.Session(config=config)

def main(numerator = 1, denominator = 1) :
    model, att_model = load_models()
    x, y = get_dataset(numerator, denominator)

    print(x[0].shape, x[1].shape)
    print(y[0].shape, y[1].shape)

    print("input note")
    print(list(x[0][0]))
    print(list(x[0][1]))

    print("input duration")
    print(list(x[1][0]))
    print(list(x[1][1]))

    print("target note")
    print(y[0])

    print("target duration")
    print(y[1])

    history = train(model, x, y)


def get_dataset(numerator, denominator):
    datas = load_data()
    tables = load_tables()

    note_data, duration_data = split_to_notes_and_durations(datas)
    dataset = create_dataset(note_data, duration_data, tables, numerator=numerator, denominator=denominator, save=False)
    return dataset

def train(model, train_x, train_y) :
    print("Model Train")

    checkpoint1 = ModelCheckpoint(
        os.path.join(MODEL_DIR, "weights-improvement-{loss:.4f}-bigger.h5"),
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )

    checkpoint2 = ModelCheckpoint(
        os.path.join(MODEL_DIR, MODEL_NAME),
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )

    early_stopping = EarlyStopping(
        monitor='loss'
        , restore_best_weights=True
        , patience=10
    )

    callbacks_list = [
        checkpoint1,
        checkpoint2,
        early_stopping
    ]

    model.save_weights(os.path.join(MODEL_DIR, MODEL_NAME))

    history = model.fit(train_x,
                         train_y,
                         epochs=200,
                         batch_size=32,
                         validation_split=0.2,
                         callbacks=callbacks_list,
                         shuffle=True)
    return history


if __name__ == '__main__':
    main()