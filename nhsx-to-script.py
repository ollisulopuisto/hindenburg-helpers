import xml.etree.ElementTree as ET
import sys

def generate_transcript(xml_file):
    """Generates a speaker-labeled transcript with timestamps from a Hindenburg PRO XML file.

    Args:
        xml_file (str): Path to the Hindenburg PRO XML file.

    Returns:
        str: The formatted transcript.
    """

    tree = ET.parse(xml_file)
    root = tree.getroot()

    audio_pool = root.find('AudioPool')
    tracks = root.find('Tracks')

    transcript = ""
    current_speaker = None

    for track in tracks.findall('Track'):
        speaker_name = track.get('Name')
        for region in track.findall('Region'):
            file_id = region.get('Ref')
            start_time = float(region.get('Start')) 
            offset = float(region.get('Offset').split(':')[1])

            # Find the corresponding audio file in the pool
            audio_file = audio_pool.find(f"./File[@Id='{file_id}']")
            transcription = audio_file.find('Transcription')

            # Extract the words within the relevant time range
            for p in transcription.findall('p'):
                for word in p.findall('w'):
                    word_start = float(word.get('s'))
                    if word_start >= offset and word_start < offset + float(region.get('Length')):
                        if current_speaker != speaker_name:
                            timestamp = f"[{int(start_time // 60):02d}:{int(start_time % 60):02d}] "
                            transcript += "\n" + timestamp + f"**{speaker_name}:** "
                            current_speaker = speaker_name 
                        transcript += word.text + " "

    return transcript


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hindenburg_transcript.py <xml_file>")
        sys.exit(1)

    xml_filepath = sys.argv[1]
    transcript = generate_transcript(xml_filepath)
    print(transcript)
