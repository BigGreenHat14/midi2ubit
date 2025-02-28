import pretty_midi
import sys
from tkinter import filedialog

def extract_main_melody(midi_file_path):
    """
    Extracts the main melody from a MIDI file and formats it as NOTE[octave][:duration].
    Rests are represented as 'r:duration' when there are gaps between notes.
    
    Parameters:
        midi_file_path (str): Path to the MIDI file.
    
    Returns:
        List[str]: List of formatted note and rest strings.
    """
    try:
        # Load the MIDI file
        midi_data = pretty_midi.PrettyMIDI(midi_file_path)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return []

    # Identify the main instrument (non-drum with the most notes)
    main_instrument = max(
        (inst for inst in midi_data.instruments if not inst.is_drum),
        key=lambda inst: len(inst.notes),
        default=None
    )

    if not main_instrument or not main_instrument.notes:
        print("No melody found in the MIDI file.")
        return []

    # Ensure the notes are sorted by start time
    sorted_notes = sorted(main_instrument.notes, key=lambda note: note.start)

    # MIDI pitch to note mapping
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    result = []
    last_end_time = 0  # Tracks when the last note ended

    for note in sorted_notes:
        pitch = note.pitch
        name = note_names[pitch % 12]
        octave = (pitch // 12) - 1  # MIDI note 60 is C4.
        
        # Calculate duration in 100ths of a second
        start_time = note.start
        duration = int(round((note.end - start_time) * 100))

        # Add a rest if there is a gap between this note and the last one
        if start_time > last_end_time:
            rest_duration = int(round((start_time - last_end_time) * 100))
            result.append(f"r:{rest_duration}")

        # Append the note
        result.append(f"{name}{octave}:{duration}")
        last_end_time = note.end

    return result


if __name__ == "__main__":
    # Allow both command-line argument and GUI file selection
    midi_path = sys.argv[1] if len(sys.argv) > 1 else filedialog.askopenfilename(filetypes=[("MIDI Files", "*.mid*")])
    
    if midi_path:
        melody = extract_main_melody(midi_path)
        print("COPY THIS:")
        print("import music")
        print("music.set_tempo(ticks=100,bpm=60) # after running this and before once, you dont have to again")
        print("music.play(" + str(melody) + ")")
    else:
        print("No file selected.")
