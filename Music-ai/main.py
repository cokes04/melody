from preprocessing import *
from model import *
from predict import *
from result import *
import tensorflow as tf

tf.debugging.set_log_device_placement(True)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('INFO')

window_size = 50

if __name__ == '__main__':
    print("main")

    data = load_data(window_size)

    #model = create_model(window_size, data.get_n_vocab())
    model = load_last_model()

    #train(model, data.input, data.output)
    midi = compose_music(model, 200, data.input, data.reverse_mapping_table)
    #show(midi)
    #listen(midi)