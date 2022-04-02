import numpy as np
from music21 import *
import os
import re
import random

generated_music_path = '../data/output'
file_name = "test_output"

def compose_music(model, note_count, input_emotion, window_size, emotion_size, reverse_mapping_table) :
    print("Compose Music")
    notes = generate_notes(model, note_count, input_emotion, window_size, emotion_size, reverse_mapping_table)
    return transform_midi(notes)

def generate_notes(model, note_count, input_emotion, window_size, emotion_size, reverse_mapping_table) :
    print("Generate Notes")

    input_emotion = float(input_emotion)
    note_size = window_size - emotion_size
    random_pattern = [random.random() for i in range(note_size)]
    emotion = [input_emotion for i in range(emotion_size)]

    pattern = random_pattern + emotion

    prediction_output = []
    n_vocab = len(reverse_mapping_table)

    for note_index in range(note_count):
        prediction_input = np.reshape(pattern, (1, len(pattern), 1))

        # 다음 note 예측
        prediction = model.predict(prediction_input, verbose=0)
        index = np.argmax(prediction) # 가장 큰 것

        result = reverse_mapping_table[index]

        #결과 저장
        prediction_output.append(result)

        #다음 패턴
        pattern = np.insert( pattern, note_size, index / float(n_vocab) )[1:]


    print("prediction :", prediction_output)

    return prediction_output

def transform_midi(output) :
    print("Note -> Midi")

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

    file_list = os.listdir(generated_music_path)

    index = 0
    if len(file_list) != 0 :
        file_list.sort(reverse=True)
        last_file = file_list[0]
        index = int(re.sub("\D", "", last_file)) + 1

    midi.write('midi', fp=f'../data/output/{file_name}_{index}.mid')

    return midi
