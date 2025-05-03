try:
    import pretty_midi
except ImportError:
    import os
    os.system("pip install pretty_midi")
    import pretty_midi
try:
    import uflash
except ImportError:
    import os
    os.system("pip install uflash")
import sys
from tkinter import filedialog, Tk, simpledialog

def extract_main_melody(midi_file_path, track_index):
    """
    Extracts the melody from a chosen MIDI track and formats it as NOTE[octave][:duration].
    When multiple notes overlap, the highest pitched note is prioritized.
    Rests are represented as 'r:duration' when there are gaps between notes.
    
    Parameters:
        midi_file_path (str): Path to the MIDI file.
        track_index (int): Index of the selected track.
    
    Returns:
        List[str]: List of formatted note and rest strings, chunked into segments.
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
    
    # Create a list of events: each note gives an "on" event and an "off" event.
    events = []
    for note in main_instrument.notes:
        events.append((note.start, 'on', note))
        events.append((note.end, 'off', note))
    
    # Sort events by time. For events at the same time, process "off" events before "on" events.
    events.sort(key=lambda x: (x[0], 0 if x[1]=='off' else 1))
    
    timeline = []
    active_notes = []
    current_time = 0.0
    
    # Helper function to get the current highest note pitch, if any.
    def highest_active():
        return max(active_notes, key=lambda n: n.pitch) if active_notes else None

    # Process events to form time segments
    for event_time, event_type, note in events:
        if event_time > current_time:
            # Determine the active note for the interval [current_time, event_time)
            current_note = highest_active()
            timeline.append((current_time, event_time, current_note))
            current_time = event_time
        
        # Update active notes based on event type
        if event_type == 'on':
            active_notes.append(note)
        elif event_type == 'off':
            if note in active_notes:
                active_notes.remove(note)
    
    # Process any leftover time if needed (not strictly necessary if MIDI ends at last note off)
    # Group consecutive segments with the same note (or rest)
    merged_segments = []
    for seg in timeline:
        start, end, note = seg
        if merged_segments and merged_segments[-1][2] == note:
            merged_segments[-1] = (merged_segments[-1][0], end, note)
        else:
            merged_segments.append(seg)
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    result = []
    
    # The time unit conversion factor (duration in hundredths of a second)
    factor = 100
    
    for seg in merged_segments:
        start, end, note = seg
        duration = int(round((end - start) * factor))
        if duration <= 0:
            continue
        if note is None:
            result.append(f"r:{duration}")
        else:
            pitch = note.pitch
            name = note_names[pitch % 12]
            octave = (pitch // 12) - 1
            result.append(f"{name}{octave}:{duration}")
    
    def chunk_list(lst, chunk_size=600):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
    
    return list(chunk_list(result))

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    
    midi_path = sys.argv[1] if len(sys.argv) > 1 else filedialog.askopenfilename(filetypes=[("MIDI Files", "*.mid*")])
    
    if midi_path:
        try:
            midi_data = pretty_midi.PrettyMIDI(midi_path)
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            sys.exit()
            
        instruments = [inst.name for inst in midi_data.instruments]
        
        if not instruments:
            print("No instruments found in the MIDI file.")
            sys.exit()
        
        track_list = "\n".join(f"{i}: {name}" for i, name in enumerate(instruments))
        print("Available Tracks:\n" + track_list)
        
        track_index = simpledialog.askinteger("Select Track", "Enter track number:", minvalue=0, maxvalue=len(instruments) - 1)
        
        if track_index is not None:
            melody = extract_main_melody(midi_path, track_index)
            program = []
            program.append("import music")
            program.append("music.set_tempo(ticks=100,bpm=60)")
            for submelody in melody:
                program.append("music.play(" + str(submelody) + ")")
            open("___miditemp.py","w").write("\n".join(program))
            import os
            os.system("uflash ___miditemp.py")
        else:
            print("No track selected.")
    else:
        print("No file selected.")
