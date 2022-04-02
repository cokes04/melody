import numpy as np
from music21 import *
import os
import re

path = './generated_music'

def compose_music(model, seq_shape, input_emotion, reverse_mapping_table) :
    notes = generate_notes(model, seq_shape, input_emotion, reverse_mapping_table)
    return transform_midi(notes)

def generate_notes(model, seq_shape, input_emotion, reverse_mapping_table) :

    music_noise = np.random.normal(0, 1, (1, seq_shape[0] - 10, seq_shape[1]))

    emotion_noise = np.ones((1, 10, seq_shape[1])) * input_emotion

    noise = np.concatenate((music_noise, emotion_noise), axis=1)

    predictions = model.predict(noise)

    pred_notes = [x * 242 + 242 for x in predictions[0]]
    pred_notes = [reverse_mapping_table[int(x)] for x in pred_notes]

    return pred_notes

def transform_midi(output) :
    offset = 0
    output_notes = []

    # note, chord 객체 생성
    for pattern in output:

        # chord 일때
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)

        # note 일떄
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        offset += 0.5

    midi = stream.Stream(output_notes)

    file_list = os.listdir(path)

    file_name = "test_output"

    index = 0
    if len(file_list) != 0 :
        file_list.sort(reverse=True)
        last_file = file_list[0]
        index = int(re.sub("\D", "", last_file)) + 1

    midi.write('midi', fp=f'./generated_music/{file_name}_{index}.mid')

    return midi
