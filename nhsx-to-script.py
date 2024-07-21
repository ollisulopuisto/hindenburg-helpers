import xml.etree.ElementTree as ET
import sys
from datetime import datetime

def time_to_seconds(time_str):
    """Converts a time string to seconds."""
    if time_str is None:
        return 0.0

    formats = ["%H:%M:%S.%f", "%M:%S.%f", "%S.%f"]  # Existing formats
    for fmt in formats:
        try:
            t = datetime.strptime(time_str, fmt)
            return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6
        except ValueError:
            pass 

    # Handle direct seconds format (e.g., "36")
    try:
        return float(time_str)
    except ValueError:
        pass

    raise ValueError(f"Invalid time string: {time_str}")

def generate_transcript(xml_file):
    """Generates a speaker-labeled transcript."""

    tree = ET.parse(xml_file)
    root = tree.getroot()

    audio_pool = root.find("AudioPool")
    tracks = root.find("Tracks")

    all_regions = []
    for track in tracks.findall("Track"):
        speaker_name = track.get("Name")
        for region in track.findall("Region"):
            file_id = region.get("Ref")
            start_time = time_to_seconds(region.get("Start"))
            offset = time_to_seconds(region.get("Offset"))
            length = time_to_seconds(region.get("Length"))
            all_regions.append((start_time, speaker_name, file_id, offset, length)) 

    all_regions.sort(key=lambda x: x[0]) 

    transcript = ""
    current_speaker = None
    seen_lines = set()  

    for start_time, speaker_name, file_id, offset, length in all_regions:
        # Find the corresponding audio file 
        audio_file = audio_pool.find(f"./File[@Id='{file_id}']")
        transcription = audio_file.find("Transcription")

        region_text = ""
        if transcription is not None:  # Check for missing transcription 
            for p in transcription.findall("p"):
                for word in p.findall("w"):
                    word_start = time_to_seconds(word.get("s"))
                    word_end = word_start + time_to_seconds(word.get("l"))

                    if (word_start >= offset and word_start < offset + length) or \
                       (word_end > offset and word_end <= offset + length) or \
                       (word_start < offset and word_end > offset + length):
                        region_text += word.text + " "

        # Timestamp and speaker name
        timestamp = f"[{int(start_time // 60):02d}:{int(start_time % 60):02d}] "
        line = timestamp + f"**{speaker_name}:** " + region_text.strip()

        if line not in seen_lines:
            if current_speaker != speaker_name:
                transcript += "\n\n" 
                current_speaker = speaker_name
            transcript += line + "\n"
            seen_lines.add(line)

    return transcript

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hindenburg_transcript.py <xml_file>")
        sys.exit(1)

    xml_filepath = sys.argv[1]
    transcript = generate_transcript(xml_filepath)
    print(transcript)