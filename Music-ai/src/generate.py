from music21 import *
import numpy as np
import argparse
import time

from dataset.load import *
from model import *

def main(emotion = "gloomy", music_len = 200, music_num = 3, noise_num = 3) :
    print("Generate Main")
    """parser = argparse.ArgumentParser(description='Generates music.')
    parser.add_argument('--emotion', default=0, type=int)
    parser.add_argument('--music_len', default=200, type=int)
    args = parser.parse_args()

    if args.emotion != None:
        emotion = EMOTIONS[args.emotion]
        print("Seleted Emotion : ", emotion)

    if args.music_len != None:
        music_len = args.music_len
        print("Seleted Music Length : ", music_len)"""

    model, att_model = load_models()
    data_for_emotion = load_data()

    note_to_int, int_to_note, duration_to_int, int_to_duration = load_tables()

    for i in range(music_num) :
        #random_index, start_notes_sequence, start_duration_sequence = get_start_random_sequence()
        random_index, start_notes_sequence, start_duration_sequence = get_start_sequence(data_for_emotion, emotion, noise_num, note_to_int, duration_to_int)
        prediction_output = generate(model, emotion, start_notes_sequence, start_duration_sequence, music_len)
        midi_stream = convert_midi(prediction_output, int_to_note, int_to_duration, emotion, random_index, save=True)
        #play_midi(midi_stream)

def convert_midi(prediction_output, int_to_note, int_to_duration, emotion, random_index, save=True) :
    print("Convert Midi")
    midi_stream = stream.Stream()
    part = stream.Part()
    midi_stream.append(part)

    for pattern in prediction_output:
        note_pattern, duration_pattern = pattern
        note_pattern = int_to_note[note_pattern]
        duration_pattern = int_to_duration[duration_pattern]
        # print( "("+note_pattern+" "+str(duration_pattern)+")" , end=' ')

        # chord
        if ('.' in note_pattern):
            notes_in_chord = note_pattern.split('.')

            """a = len(notes_in_chord) // 4
            for i in range(a+1) :
                chord_notes = []
                for n in notes_in_chord[i * 4: (i + 1) * 4] :
                    new_note = note.Note(n)
                    new_note.duration = duration.Duration(duration_pattern)
                    new_note.storedInstrument = instrument.Piano()
                    chord_notes.append( new_note )

                if len(chord_notes) != 0:
                    part.append(chord.Chord(chord_notes))"""

            chord_notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(current_note)
                new_note.duration = duration.Duration(duration_pattern)
                new_note.storedInstrument = instrument.Violoncello()
                chord_notes.append(new_note)
            new_chord = chord.Chord(chord_notes)
            part.append(new_chord)

        elif note_pattern == 'rest':
            # rest
            new_note = note.Rest()
            new_note.duration = duration.Duration(duration_pattern)
            new_note.storedInstrument = instrument.Piano()
            part.append(new_note)
        elif note_pattern != 'START':
            # note
            new_note = note.Note(note_pattern)
            new_note.duration = duration.Duration(duration_pattern)
            new_note.storedInstrument = instrument.Piano()
            part.append(new_note)


    #print()
    midi_stream = midi_stream.chordify()
    if save :
        timestr = time.strftime("%Y%m%d-%H%M%S")
        midi_stream.write('midi', fp=os.path.join(OUTPUT_DIR, f'{emotion}-{random_index}-{timestr}.mid'))

    return midi_stream

def play_midi(midi_stream) :
    print("Play Midi")
    midi_stream.show("midi")

def sample_with_temp(preds, temperature = 0.5):

    if temperature == 0:
        return np.argmax(preds)
    else:
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        return np.random.choice(len(preds), p=preds)

def get_start_random_sequence(timestep = SEQ_LEN) :
    print("random start")
    notes_sequence = np.random.randint(NUM_NOTES, size=timestep)
    durations_sequence = np.random.randint(NUM_DURATION, size=timestep)

    #print("input note : ", notes_sequence)

    return -1, list(notes_sequence), list(durations_sequence)

def get_start_sequence(data_for_emotion : dict, emotion, noise_num, note_to_int, duration_to_int, timestep = SEQ_LEN) :
    assert noise_num <= timestep

    data = data_for_emotion[emotion]

    def get_random_index() :
        random_index = np.random.randint(len(data[0]), size = 1)[0]
        assert len(data[0][random_index]) >= SEQ_LEN
        assert len(data[1][random_index]) >= SEQ_LEN
        return random_index

    while True :
        try:
            random_index = get_random_index()
            break
        except :
            continue
    print("random index : ", random_index)

    notes_sequence = data[0][random_index][:SEQ_LEN]
    durations_sequence = data[1][random_index][:SEQ_LEN]

    random_noise_indexs = np.random.randint(len(notes_sequence), size = noise_num)
    for i in random_noise_indexs :
        notes_sequence[i] = 'START'
        #durations_sequence[i] = 0

    #print("input note : ", notes_sequence)

    notes_sequence = [note_to_int[n] for n in notes_sequence]
    durations_sequence = [duration_to_int[b] for b in durations_sequence]

    return random_index, notes_sequence, durations_sequence

def generate(model, emotion, start_notes_sequence, start_duration_sequence, music_len = 500, timestep = SEQ_LEN) :
    print("Generate Music")

    temp = {
        "delighted" : (0.75, 0),
        "gloomy" : (0, 1.25),
        "relaxed" : (0.5, 0.5),
        }

    notes_temp, duration_temp = temp[emotion]

    notes_input_sequence = start_notes_sequence
    durations_input_sequence = start_duration_sequence

    prediction_output = []

    for note_index in range(music_len):
        prediction_input = [np.array([notes_input_sequence]), np.array([durations_input_sequence])]

        notes_prediction, durations_prediction = model.predict(prediction_input, verbose=0)

        i1 = sample_with_temp(notes_prediction[0], notes_temp)
        i2 = sample_with_temp(durations_prediction[0], duration_temp)

        prediction_output.append([i1, i2])

        notes_input_sequence.append(i1)
        durations_input_sequence.append(i2)

        notes_input_sequence = notes_input_sequence[1:]
        durations_input_sequence = durations_input_sequence[1:]

    return prediction_output


if __name__ == '__main__':
    main()