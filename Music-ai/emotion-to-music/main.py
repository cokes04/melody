from preprocessing import *
from model import *
from predict import *
import tensorflow as tf

tf.debugging.set_log_device_placement(True)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('INFO')

window_size = 10

if __name__ == '__main__':
    print("main")

    train_x, train_y, mapping_table, reverse_mapping_table = get_dataset(window_size, is_save=True)
    print(mapping_table)
    print(reverse_mapping_table)
    print(train_x)
    print(train_y)

    #model = create_model()