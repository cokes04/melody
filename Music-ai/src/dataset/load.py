from constants import *
import pickle

def load_dataset() :
    print("Load Dataset")
    x, y = load('dataset')
    return x, y

def load_data() :
    print("Load Data")
    data_for_emotion = load('data')
    return data_for_emotion

def load_tables() :
    print("Load Table")
    note_to_int, int_to_note, duration_to_int, int_to_duration = load('table')
    return note_to_int, int_to_note, duration_to_int, int_to_duration

def load_distinct() :
    print("Load Distinct")
    note_names, duration_names = load('distinct')
    return note_names, duration_names

def load(fname) :
    with open(f'{DATASET_DIR}/{fname}', 'rb') as filepath:
        file = pickle.load(filepath)
    return file