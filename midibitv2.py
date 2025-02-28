import pretty_midi
import sys
from tkinter import filedialog, Tk, simpledialog

def extract_main_melody(midi_file_path, track_index):
    """
    Extracts the melody from a chosen MIDI track and formats it as NOTE[octave][:duration].
    Rests are represented as 'r:duration' when there are gaps between notes.
    
    Parameters:
        midi_file_path (str): Path to the MIDI file.
        track_index (int): Index of the selected track.
    
    Returns:
        List[str]: List of formatted note and rest strings.
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file_path)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return []

    if track_index < 0 or track_index >= len(midi_data.instruments):
        print("Invalid track selection.")
        return []
    
    main_instrument = midi_data.instruments[track_index]
    
    if not main_instrument.notes:
        print("No melody found in the selected track.")
        return []

    sorted_notes = sorted(main_instrument.notes, key=lambda note: note.start)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    result = []
    last_end_time = 0

    for note in sorted_notes:
        pitch = note.pitch
        name = note_names[pitch % 12]
        octave = (pitch // 12) - 1
        start_time = note.start
        duration = int(round((note.end - start_time) * 100))
        
        if start_time > last_end_time:
            rest_duration = int(round((start_time - last_end_time) * 100))
            result.append(f"r:{rest_duration}")
        
        result.append(f"{name}{octave}:{duration}")
        last_end_time = note.end
    
    def chunk_list(lst, chunk_size=600):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
    
    return list(chunk_list(result))

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    
    midi_path = sys.argv[1] if len(sys.argv) > 1 else filedialog.askopenfilename(filetypes=[("MIDI Files", "*.mid*")])
    
    if midi_path:
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        instruments = [inst.name for inst in midi_data.instruments]
        
        if not instruments:
            print("No instruments found in the MIDI file.")
            sys.exit()
        
        track_list = "\n".join(f"{i}: {name}" for i, name in enumerate(instruments))
        print("Available Tracks:\n" + track_list)
        
        track_index = simpledialog.askinteger("Select Track", "Enter track number:", minvalue=0, maxvalue=len(instruments) - 1)
        
        if track_index is not None:
            melody = extract_main_melody(midi_path, track_index)
            print("COPY THIS:")
            print("import music")
            print("music.set_tempo(ticks=100,bpm=60) # Run this once before playing")
            for submelody in melody:
                print("music.play(" + str(submelody) + ")")
        else:
            print("No track selected.")
    else:
        print("No file selected.")
