from music21 import *
import numpy as np
import tensorflow.keras.utils as np_utils
from functools import reduce
import pickle
import math
import os

from dataset.load import *
from util import *

def main() :
    print("Crate Dataset Main")
    data_for_emotion, note_names, duration_names = create_data()
    tables = create_tables(note_names, duration_names)

def split(data, time_steps, n, denominator):
    # n/denominator 나눠서 학습
    assert n<=denominator

    dataX, dataY = [], []

    for i in range(0, len(data) -(n-1+time_steps), denominator):
        a = i + n - 1
        dataX.append(data[a : a + time_steps])
        dataY.append(data[a + time_steps])

    return dataX, dataY

def split_to_notes_and_durations(data_for_emotion) :
    note_data = []
    duration_data = []
    for ns, ds in data_for_emotion.values() :
        note_data += ns
        duration_data += ds

    return note_data, duration_data

def insertStreamAtt(a, b) :
    a.atSoundingPitch = b.atSoundingPitch
    a.clef = b.clef
    a.duration = b.duration
    #a.elements = b.elements
    a.finalBarline = b.finalBarline
    a.keySignature = b.keySignature
    a.metadata = b.metadata
    a.seconds = b.seconds
    a.staffLines = b.staffLines
    a.timeSignature = b.timeSignature

def insertMusic21ObectAtt(a, b) :
    try:
        a.activeSite = b.activeSite
    except :
        None
    a.derivation = b.derivation
    a.editorial = b.editorial
    a.offset = b.offset
    a.priority = b.priority
    a.quarterLength = b.quarterLength
    a.style = b.style

def get_seq(mu, chordify = True) :
    notes = []
    durations = []

    if chordify :
        elements = mu.chordify().transpose(1).flat
    else:
        elements = mu.flat.notes.recurse()

    aa = stream.Stream()
    pp = stream.Part()
    aa.append(pp)

    for element in elements :
        pp.append(element)
        if isinstance(element, note.Note):
            if element.isRest:
                notes.append(str(element.name))
                durations.append(element.duration.quarterLength)
            else:
                notes.append(str(element.nameWithOctave))
                durations.append(element.duration.quarterLength)

        elif isinstance(element, chord.Chord):
            a = len(element.pitches) // 4
            for i in range(a+1) :
                n = '.'.join(n.nameWithOctave for n in element.pitches[i*4 : (i+1)*4])
                if n != '':
                    notes.append(n)
                    durations.append(element.duration.quarterLength)

            #notes.append('.'.join(n.nameWithOctave for n in element.pitches))
            #durations.append(element.duration.quarterLength)

    aa.write('midi', fp='../../abc.midi')
    raise Exception
    assert len(notes) == len(durations)
    return notes, durations

def get_seqs(midi_dir) :
    seqs = []

    for root, dirs, files in os.walk(midi_dir):
        length = len(files)/6
        print(length)
        i = 0
        for f in files :
            i += 1
            if i > length :
                break
            try:
                fname = os.path.join(root, f)
                song = converter.parse(fname)
                print(f"Read Success: {fname}")
            except :
                print(f"Read Failed: {fname}")
                continue

            seq = get_seq(song)
            seqs.append(seq)

    return seqs

def create_data(dir = DATA_DIR, emotions = EMOTIONS, includ_etc = False, save = True) :
    print("Create Data")

    data_for_emotion = dict()

    note_names = set()
    duration_names = set()

    if includ_etc :
        emotions.append("etc")
    for i, emotion in enumerate(emotions) :
        path = os.path.join(dir, emotion)
        print("@@@@@@@@@@@@@@@@@@@@@@")
        print(path)
        seqs = get_seqs(path)

        note_data = []
        duration_data = []

        for seq in seqs :
            notes, durations = seq
            note_data.append(notes)
            duration_data.append(durations)
            note_names.update(notes)
            duration_names.update(durations)

        data_for_emotion[emotion] = note_data, duration_data

    note_names.add("START")
    note_num = len(note_names)
    duration_num = len(duration_names)
    print( "NOTE_NUM : ", note_num )
    print( "DURATION_NUM : ", duration_num )


    if save :
        with open(f'{DATASET_DIR}/data', 'wb') as filepath:
            pickle.dump( data_for_emotion , filepath )

        with open(f'{DATASET_DIR}/distinct', 'wb') as filepath:
            pickle.dump( (note_names, duration_names) , filepath )

    return data_for_emotion, note_names, duration_names

def create_distinct(note_data, duration_data, save = True) :
    note_names = sorted(set(reduce(lambda l1, l2 : l1 + l2, note_data, [])))
    duration_names = sorted(set(reduce(lambda l1, l2 : l1 + l2, duration_data, [])))

    note_num = len(note_names)
    duration_num = len(duration_names)
    print( "NOTE_NUM : ", note_num )
    print( "DURATION_NUM : ", duration_num )

    if save :
        with open(f'{DATASET_DIR}/distinct', 'wb') as filepath:
            pickle.dump( (note_names, duration_names) , filepath )

    return note_names, duration_names

def create_table(set, start = 0) :
    element_to_int = dict((element, index + start) for index, element in enumerate(set))
    int_to_element = dict((index + start, element) for index, element in enumerate(set))

    return (element_to_int, int_to_element)

def create_tables(note_names, duration_names, save = True) :
    note_names.remove("START")
    
    note_to_int, int_to_note = create_table(sorted(list(note_names)), 1)
    duration_to_int, int_to_duration = create_table(sorted(list(duration_names)))

    note_names.add("START")
    note_to_int['START'] = 0
    int_to_note[0] = 'START'

    if save :
        with open(f'{DATASET_DIR}/table', 'wb') as filepath:
            pickle.dump( (note_to_int, int_to_note, duration_to_int, int_to_duration) , filepath )

    return note_to_int, int_to_note, duration_to_int, int_to_duration

def create_dataset(note_data, duration_data, tables, time_steps = SEQ_LEN, numerator=1, denominator=1,  save = True) :
    print("Create Dataset")
    note_to_int, int_to_note, duration_to_int, int_to_duration = tables

    note_input = []
    duration_input = []
    note_target = []
    duration_target = []

    for notes, durations in zip(note_data, duration_data) :
        note_buffer = [note_to_int[n] for n in notes]
        duration_buffer = [duration_to_int[d] for d in durations]

        note_train, note_label = split(note_buffer, time_steps, numerator, denominator)
        note_input += note_train
        note_target += note_label

        duration_train, duration_label = split(duration_buffer, time_steps, numerator, denominator)
        duration_input += duration_train
        duration_target += duration_label

    note_input = np.array(note_input)
    duration_input = np.array(duration_input)

    note_target = np_utils.to_categorical(note_target, num_classes=len(note_to_int))
    duration_target = np_utils.to_categorical(duration_target, num_classes=len(duration_to_int))

    print(note_input.shape, duration_input.shape)
    print(note_target.shape, duration_target.shape)

    assert len(note_input) == len(duration_input)
    assert len(duration_input) == len(note_target) == len(duration_target)

    x = [note_input, duration_input]
    y = [note_target, duration_target]

    if save :
        with open(f'{DATASET_DIR}/dataset', 'wb') as filepath:
            pickle.dump( (x, y) , filepath )

    return (x, y)

if __name__ == '__main__':
    main()


