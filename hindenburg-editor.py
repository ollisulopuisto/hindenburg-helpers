import xml.etree.ElementTree as ET
import re
from datetime import timedelta

# ==============================================================================
# 1. DATA MODEL CLASSES (based on spec.md)
# ==============================================================================

class Session:
    """Represents the entire Hindenburg project session."""
    def __init__(self, audio_files=None, tracks=None, markers=None):
        self.audio_files = audio_files or []
        self.tracks = tracks or []
        self.markers = markers or []

class AudioFile:
    """Represents a single audio file from the AudioPool."""
    def __init__(self, id, name, duration, words=None):
        self.id = id
        self.name = name
        self.duration = duration
        self.words = words or []

class Word:
    """Represents a single transcribed word."""
    def __init__(self, text, start_time, length):
        self.text = text
        self.start_time = start_time
        self.length = length

class Track:
    """Represents a single track on the timeline."""
    def __init__(self, name, regions=None):
        self.name = name
        self.regions = regions or []

class Region:
    """Represents a single region (clip) on a track."""
    def __init__(self, source_file_id, start_time, length, offset, muted=False):
        self.source_file_id = source_file_id
        self.start_time = start_time
        self.length = length
        self.offset = offset
        self.muted = muted

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def time_to_seconds(time_str):
    """Converts Hindenburg time format (e.g., "HH:MM:SS.sss") to seconds."""
    if not time_str:
        return 0.0
    parts = re.split('[:.]', time_str)
    seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    if len(parts) > 3:
        seconds += float(f"0.{parts[3]}")
    return seconds

def seconds_to_time(seconds):
    """Converts seconds to Hindenburg time format (e.g., "HH:MM:SS.sss")."""
    td = timedelta(seconds=seconds)
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

# ==============================================================================
# 3. CORE LOGIC: PARSING AND WRITING
# ==============================================================================

def parse_hindenburg_xml(file_path):
    """Parses a Hindenburg .xml file and builds the object model."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Parse AudioPool
    audio_files = []
    for audio_elem in root.findall(".//AudioFile"):
        file_id = audio_elem.get("Id")
        name = audio_elem.get("Name")
        duration = time_to_seconds(audio_elem.get("Duration"))
        
        words = []
        for word_elem in audio_elem.findall(".//w"):
            text = word_elem.text
            start = time_to_seconds(word_elem.get("s"))
            length = time_to_seconds(word_elem.get("l"))
            words.append(Word(text, start, length))
            
        audio_files.append(AudioFile(file_id, name, duration, words))

    # Parse Tracks
    tracks = []
    for track_elem in root.findall(".//Track"):
        name = track_elem.get("Name")
        
        regions = []
        for region_elem in track_elem.findall(".//Region"):
            source_id = region_elem.get("Ref")
            start = time_to_seconds(region_elem.get("Start"))
            length = time_to_seconds(region_elem.get("Length"))
            offset = time_to_seconds(region_elem.get("Offset"))
            muted = region_elem.get("Muted") == "1"
            regions.append(Region(source_id, start, length, offset, muted))
            
        tracks.append(Track(name, regions))

    return Session(audio_files, tracks)

def write_hindenburg_xml(session, output_path):
    """Writes the session object model back to a Hindenburg .xml file."""
    # This is a complex task. For now, we'll just create a placeholder.
    # A full implementation would need to rebuild the XML tree from the session object.
    print(f"Placeholder: Writing session to {output_path}")
    # In a real implementation, you would use ElementTree to build a new XML
    # document and then write it to a file.
    pass

# ==============================================================================
# 4. EDITING LOGIC
# ==============================================================================

def delete_words(session, word_to_delete):
    """
    Finds all occurrences of a word, splits them into their own regions,
    and then deletes those regions.
    """
    print(f"Starting deletion process for word: '{word_to_delete}'")
    
    # This is where the core logic for your request will go.
    # It will involve:
    # 1. Iterating through tracks and their regions.
    # 2. Finding the corresponding audio file and its words.
    # 3. Identifying which words fall within a region's timeframe.
    # 4. If a target word is found, "splitting" the region into up to three parts:
    #    - The part before the word.
    #    - The part containing the word.
    #    - The part after the word.
    # 5. Removing the region that contains the target word.
    # 6. Adjusting the start times and lengths of the remaining regions.
    
    print("Word deletion logic not yet implemented.")
    return session


# ==============================================================================
# 5. MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    # Example usage:
    # 1. Provide path to your Hindenburg XML file.
    # 2. Specify the word you want to delete.
    # 3. Provide the path for the new, modified XML file.
    
    input_file = "path/to/your/session.xml"
    output_file = "path/to/your/modified_session.xml"
    word_to_remove = "kissa"

    try:
        # Step 1: Parse the XML into our object model
        print(f"Parsing {input_file}...")
        session = parse_hindenburg_xml(input_file)
        print("Parsing complete.")

        # Step 2: Apply the editing logic
        modified_session = delete_words(session, word_to_remove)

        # Step 3: Write the modified object model back to a new XML file
        print(f"Writing modified session to {output_file}...")
        write_hindenburg_xml(modified_session, output_file)
        print("Done.")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'.")
        print("Please update the 'input_file' variable with the correct path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

