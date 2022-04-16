from model import *
from constants import *

def train(model, train_x, train_y) :
    print("Model Train")

    checkpoint = ModelCheckpoint(
        Model_PATH,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    history = model.fit(train_x, train_y, epochs=10000, batch_size=64, callbacks=callbacks_list)
    return history

if __name__ == '__main__':
    model = load_model()
    x, y = load_dataset()
    train(model, x, y)