import os
import csv
import pickle
import glob
import logging
import numpy as np
from music21 import *
import tensorflow.keras.utils as np_utils

logging.basicConfig(level=logging.INFO)
input_data_path = "../data/input/EMOPIA_2"

window_size = 50
emotion_size = 5

def load_dataset(window_size = 50, emotion_size = 5) :
    logging.info("Load Dataset")

    with open(f'{input_data_path}/data/dataset', 'rb') as filepath:
        notes_to_emotion = pickle.load(filepath)

    with open(f'{input_data_path}/data/dataset_mapping_table', 'rb') as filepath:
        mapping_table, reverse_mapping_table = pickle.load(filepath)

    train_x, train_y = prepare_data(notes_to_emotion, mapping_table, window_size, emotion_size)

    return (train_x, train_y, mapping_table, reverse_mapping_table)

def create_dataset(window_size = 50, emotion_size = 5) :
    logging.info("Create Dataset")

    notes_to_emotion = []
    mapping_table, reverse_mapping_table, song_to_notes = get_notes()
    song_to_emotions = get_emotions()

    logging.info("Notes To Emotion")
    for name, notes in song_to_notes.items():
        if name in song_to_emotions:
            notes_to_emotion.append((notes, song_to_emotions[name]))
        else: logging.warning(f"{name} : Emotion Is Null")

    train_x, train_y = prepare_data(notes_to_emotion, mapping_table, window_size, emotion_size)

    logging.info("Save Dataset")
    with open(f'{input_data_path}/data/dataset', 'wb') as filepath:
        pickle.dump(notes_to_emotion, filepath)

    with open(f'{input_data_path}/data/dataset_mapping_table', 'wb') as filepath:
        pickle.dump((mapping_table, reverse_mapping_table), filepath)

    return (train_x, train_y, mapping_table, reverse_mapping_table)


def prepare_data(notes_to_emotion, mapping_table, window_size, emotion_size) :
    train_x, train_y = [], []

    n_vocab = len(mapping_table)

    for notes, emotion in notes_to_emotion:
        for i in range(0, len(notes) - window_size + emotion_size, 1):
            #INPUT # 입력 데이터 : [note, note, note, ........., 감정, 감정, 감정, 감정, 감정]
            input = []
            for note in notes[i:i + window_size - emotion_size] : input.append(mapping_table[note])
            for k in range(emotion_size) : input.append(emotion)
            train_x.append(input)

            #OUTPUT
            sequence_out = notes[i + window_size - emotion_size]
            train_y.append(mapping_table[sequence_out])
            #print(f'{input} -> {mapping_table[sequence_out]}')

    train_x = normalize_x(train_x, n_vocab, window_size)
    train_y = np_utils.to_categorical(train_y)

    return (train_x, train_y)

def get_emotions():
    logging.info("Read Emotion CSV")
    with open(f'{input_data_path}/emotions.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        song_to_emotion = {}

        for row in csv_reader:
            song_to_emotion[row["name"]] = float(row["emotion"])

        return song_to_emotion

def get_notes() :
    note_set = set()
    song_to_notes = {}

    logging.info("Read MIDI Files")

    for file in glob.glob(f'{input_data_path}/midis/*.mid'):
        # 경로 및 확장자 제거
        file_name, extension = os.path.splitext( os.path.basename(file) )

        #midi파일을 music21 객체(stream.Score)로 바꿈
        try:
            midi = converter.parse(file)
            logging.info(f"Parse Success: {file_name}")
        except :
            logging.warning(f"Parse Failed: {file_name}")
            continue

        notes_of_song = get_notes_of_song(midi)
        song_to_notes[file_name] = notes_of_song # { 파일명 : [note,note,note,note,note,note], .....}
        note_set.update(notes_of_song)

    mapping_table, reverse_mapping_table = get_note_table(note_set)

    return mapping_table, reverse_mapping_table, song_to_notes


def get_notes_of_song(midi) :
    notes = []
    # 악기별로 파트 분할
    try:
        song = instrument.partitionByInstrument(midi)
        notes_to_parse = song.parts
    except:  # file has notes in a flat structure
        notes_to_parse = [midi.flat.notes]

    for part in notes_to_parse:
        for element in part.recurse():
            #pitch
            # 계이름 / 도 : C, 레 : D, 미 : E ........
            # 변화표 / # : 반음 up, - : 반음 down
            # 옥타브 / 1 ~ 8 정수

            # Note인 경우 pitch 1개 가짐 ex) C#4
            if isinstance(element, note.Note):
                #print(f'{str(element.pitch)} ===== {element.pitch.name}{element.pitch.implicitOctave}')
                notes.append(str(element.pitch))

            #Chord(화음)인 경우 pitch 여러개 가짐
            #pitch는 정수 형태로 pitch.pitch.pitch와 같은 형태로 저장 # ex) 7.11.2
            elif isinstance(element, chord.Chord):
                notes.append(".".join(str(n) for n in element.normalOrder))

            # 기타 등등은 버림
            else : continue

    return notes

def get_note_table(note_set : set) :
    # 나올 수 있는 값들 정렬
    can = sorted(list(note_set))
    mapping_table = dict()
    reverse_mapping_table = dict()

    for index, c in enumerate(can) :
        # 각 값에 번호 매김  ex) { '3' : 0, '0.3.6': 1, 'G#4': 2, 'G3': 3}
        mapping_table[c] = index
        # mapping에서 key, value 반대 ex) { 0 : '3', 1 : '0.3.6', 2 : 'G#4', 3 : 'G3'}
        reverse_mapping_table[index] = c

    return mapping_table, reverse_mapping_table

# 0 ~ 1 사이로 정규화
def normalize_x(x, n_vocab, window_size) :
    n_patterns = len(x)
    return np.reshape(x, (n_patterns, window_size, 1)) / float(n_vocab)


def get_seq_shape() :
    return (window_size, 1)

def get_n_vocab() :
    with open(f'{input_data_path}/data/dataset_mapping_table', 'rb') as filepath:
        mapping_table, reverse_mapping_table = pickle.load(filepath)
        return len(mapping_table)

if __name__ == '__main__':
    logging.info("Preprocessing Data")
    create_dataset(window_size, emotion_size)