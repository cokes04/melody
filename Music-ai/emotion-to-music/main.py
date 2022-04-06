from preprocessing import *
from model import *
from predict import *
import tensorflow as tf
import logging

logging.basicConfig(level=logging.INFO)
tf.debugging.set_log_device_placement(True)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('INFO')

if __name__ == '__main__':
    logging.info("Main")

    train_x, train_y, mapping_table, reverse_mapping_table = load_dataset()
    model = load_last_model()
    
    #history = train(model, train_x, train_y, epochs=100)
    #show_train_result(history, is_save=True)

    note_count = 500
    input_emotion = 4
    compose_music(model, note_count, input_emotion, reverse_mapping_table)
