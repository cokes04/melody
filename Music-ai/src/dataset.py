import os
import csv
import pickle
import glob
import numpy as np
from music21.midi import MidiFile, ChannelVoiceMessages, MetaEvents

import tensorflow.keras.utils as np_utils

from constants import *
from util import *

def compute_beat(beat, notes_in_bar):
    return one_hot(beat % notes_in_bar, notes_in_bar)

def stagger(data, in_time_steps, out_time_steps):
    dataX, dataY = [], []

    for i in range(0, len(data) - ( in_time_steps + out_time_steps) , NOTES_PER_BAR):
        dataX.append(data[i:i + in_time_steps])
        dataY.append(data[i + in_time_steps : i + in_time_steps + out_time_steps])

    return dataX, dataY

def open_midi(fname) :
    mf = MidiFile()
    mf.open(filename=fname)
    mf.read()
    mf.close()
    return mf

def get_seq(song) :
    times = []
    notes = []

    for track in song.tracks :
        buffer = None
        for i in range(0, len(track.events), 2):
            deltaTime = track.events[i]
            midiEvent = track.events[i+1]

            if deltaTime.time != 0 \
                    and midiEvent.type is ChannelVoiceMessages.NOTE_ON \
                    or midiEvent.type is ChannelVoiceMessages.NOTE_OFF:
                times.append(deltaTime.time)
                if buffer is not None :
                    notes.append(buffer)
                buffer = np.zeros(NUM_NOTES)

            if midiEvent.type is ChannelVoiceMessages.NOTE_ON:
                buffer[midiEvent.pitch] = midiEvent.velocity if midiEvent.velocity != 0 else -1

            elif midiEvent.type is ChannelVoiceMessages.NOTE_OFF:
                buffer[midiEvent.pitch] = -1

            elif midiEvent.type is MetaEvents.END_OF_TRACK :
                if buffer is not None :
                    notes.append(buffer)

    #for t, n in zip(times, notes) :
    #    print(t, n)

    return (times, notes)

def get_seqs(midi_dir) :
    print("Read Midi")
    seqs = []

    for root, dirs, files in os.walk(midi_dir):
        for f in files :
            try:
                fname = os.path.join(root, f)
                song = open_midi(fname)
                print(f"Read Success: {fname}")
            except :
                print(f"Read Failed: {fname}")
                continue

            seq = get_seq(song)
            seqs.append(seq)

    return seqs

def create_dataset(in_time_steps = IN_SEQ_LEN , out_time_steps = OUT_SEQ_LEN) :
    print("Create Dataset")

    note_data = []
    time_data = []
    emotion_data = []

    note_target = []
    time_target = []

    for i, emotion in enumerate(EMOTIONS) :
        path = f"{DATA_DIR}/{emotion}"
        seqs = get_seqs(path)
        emotion = one_hot(i, NUM_EMOTION)

        for seq in seqs :
            if len(seq[0]) < in_time_steps + out_time_steps : continue
            times, notes = seq
            print(len(times), len(notes))

            note_train, note_label = stagger(notes, in_time_steps, out_time_steps)
            note_data += note_train
            note_target += note_label

            time_train, time_label = stagger(times, in_time_steps, out_time_steps)
            time_data += time_train
            time_target += time_label

            emotion_data = [emotion for _ in range(len(seq[0]))]

    note_data = np.array(note_data)
    time_data = np.array(time_data)
    emotion_data = np.array(emotion_data)

    print(note_data.shape, time_data.shape, emotion_data.shape)

    note_target = np.array(note_target)
    time_target = np.array(time_target)
    print(note_target.shape, time_target.shape)

    x = [note_data, time_data, emotion_data]
    y = [note_target, time_target]

    with open(f'{DATASET_DIR}/dataset', 'wb') as filepath:
        pickle.dump( (x,y) , filepath)


    assert len(x[0]) == len(x[1])
    assert len(x[0]) == len(y[0])
    assert len(y[0]) == len(y[1])

    return x, y

def load_dataset() :
    print("Load Dataset")
    with open(f'{DATASET_DIR}/dataset', 'rb') as filepath:
        x, y = pickle.load(filepath)

    return x, y

if __name__ == '__main__':
    print("Dataset Main")
    create_dataset()