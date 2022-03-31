import pickle
import glob
import numpy as np
from music21 import *
import tensorflow.keras.utils as np_utils


filepath = 'data/'

class Data :
    def __init__(self, mapping_table : dict,
                 reverse_mapping_table: dict,
                 input : np.ndarray,
                 output : list):
        self.mapping_table = mapping_table
        self.reverse_mapping_table = reverse_mapping_table
        self.input = input
        self.output = output

    def get_n_vocab(self) :
        return len(self.mapping_table)

def load_data(window_size) :
    print("Load Data")

    with open('data/songs', 'rb') as filepath:
        songs = pickle.load(filepath)
        note_set = set()
        for song in songs :
            note_set.update(song)
        mapping_table, reverse_mapping_table = get_table(note_set)
        input, output = get_in_out_data(songs, mapping_table, window_size)

        n_vocab = len(note_set)
        input, output = normalize(input, output, n_vocab, window_size)

        return Data(mapping_table, reverse_mapping_table, input, output)

def get_data(window_size) :
    note_set = set()
    songs = []
    print("Load Data")

    for file in glob.glob("./input_music/*.mid"):
        #midi파일을 music21 객체(stream.Score)로 바꿈
        try:
            midi = converter.parse(file)
            print(f"Parse Success : {str(file.title())}")
        except :
            print(f"Parse Failed : {str(file.title())}")
            continue

        notes = get_notes(midi)
        songs.append(notes)
        note_set.update(notes)

    mapping_table, reverse_mapping_table = get_table(note_set)
    input, output = get_in_out_data(songs, mapping_table, window_size)

    n_vocab = len(note_set)
    input, output = normalize(input, output, n_vocab, window_size)

    with open('data/songs', 'wb') as filepath:
        pickle.dump(songs, filepath)

    return Data(mapping_table, reverse_mapping_table, input, output)

def get_notes(midi) :
    notes = []
    # 악기별로 파트 분할
    song = instrument.partitionByInstrument(midi)

    parts = song.parts[0:]
    for part in parts:
        for element in part.recurse():
            #pitch
            # 계이름 / 도 : C, 레 : D, 미 : E ........
            # 변화표 / # : 반음 up, - : 반음 down
            # 옥타브 / 1 ~ 8? 정수

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


def get_table(note_set : set) :
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


def get_in_out_data(songs, mapping_table, window_size) :
    input = []
    output = []

    for song in songs :
        for i in range(0, len(song) - window_size, 1) :
            sequence_in = song[i : i + window_size]
            sequence_out = song[i + window_size]
            #print(f'{sequence_in}  -> {sequence_out}')

            input.append( [mapping_table[c] for c in sequence_in] )
            output.append( mapping_table[sequence_out] )

    return input, output

def normalize(input, output, n_vocab, window_size) :
    n_patterns = len(input)

    input = np.reshape(input, (n_patterns, window_size, 1)) / float(n_vocab)
    output = np_utils.to_categorical(output)

    return input, output