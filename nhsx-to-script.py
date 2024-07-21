import xml.etree.ElementTree as ET
import sys

def time_to_seconds(time_str):
    """Converts a time string in the format MM:SS.sss or SS.sss to seconds.

    Args:
        time_str (str): The time string.

    Returns:
        float: Time in seconds.
    """
    if time_str is None:
        return 0.0

    parts = time_str.split(":")
    if len(parts) == 2:
        minutes, seconds = map(float, parts)
        return minutes * 60 + seconds
    elif len(parts) == 1:
        return float(parts[0])
    else:
        raise ValueError(f"Invalid time string: {time_str}")

def generate_transcript(xml_file):
    """Generates a speaker-labeled transcript from a Hindenburg PRO XML file.

    Args:
        xml_file (str): Path to the Hindenburg PRO XML file.

    Returns:
        str: The formatted transcript.
    """

    tree = ET.parse(xml_file)
    root = tree.getroot()

    audio_pool = root.find("AudioPool")
    tracks = root.find("Tracks")

    transcript = ""
    current_speaker = tracks.find("Track").get("Name")  # Set initial speaker

    for track in tracks.findall("Track"):
        speaker_name = track.get("Name")
        for region in track.findall("Region"):
            file_id = region.get("Ref")
            region_start_time = time_to_seconds(region.get("Start"))
            offset = time_to_seconds(region.get("Offset"))
            length = time_to_seconds(region.get("Length"))

            # Find the corresponding audio file in the pool
            audio_file = audio_pool.find(f"./File[@Id='{file_id}']")
            transcription = audio_file.find("Transcription")

            # Extract the relevant portion of the transcription
            region_text = ""
            for p in transcription.findall("p"):
                for word in p.findall("w"):
                    word_start = time_to_seconds(word.get("s"))
                    word_end = word_start + time_to_seconds(word.get("l"))

                    # Check if word (or part of it) is within the region
                    if (word_start >= offset and word_start < offset + length) or \
                       (word_end > offset and word_end <= offset + length) or \
                       (word_start < offset and word_end > offset + length):
                        region_text += word.text + " "

            # Add timestamp and speaker name for each region
            timestamp = f"[{int(region_start_time // 60):02d}:{int(region_start_time % 60):02d}] "
            if current_speaker != speaker_name:
                transcript += "\n\n"  # Add extra line break for new speaker
                current_speaker = speaker_name
            transcript += timestamp + f"**{speaker_name}:** " + region_text

    transcript += "\n"
    return transcript

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hindenburg_transcript.py <xml_file>")
        sys.exit(1)

    xml_filepath = sys.argv[1]
    transcript = generate_transcript(xml_filepath)
    print(transcript)
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hindenburg_transcript.py <xml_file>")
        sys.exit(1)

    xml_filepath = sys.argv[1]
    transcript = generate_transcript(xml_filepath)
    print(transcript)