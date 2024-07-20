import json
import datetime

def format_timestamp(timestamp):
  """Formats a timestamp in seconds to HH:MM:SS format."""
  return str(datetime.timedelta(seconds=timestamp))

def json_to_markdown(json_data):
  """Converts JSON transcript data to Markdown format."""
  markdown = ""
  current_speaker = None
  current_paragraph = []

  for i, segment in enumerate(json_data['segments']):
    speaker = segment['speaker']
    start_time = format_timestamp(segment['startTime'])
    end_time = format_timestamp(segment['endTime'])
    body = segment['body']

    if speaker != current_speaker:
      # New speaker, start a new paragraph
      if current_paragraph:
        markdown += f"{current_speaker}: {current_paragraph}\n\n"
      current_speaker = speaker
      current_paragraph = [f"{start_time}-{end_time} {body}"]
    else:
      # Same speaker, add to current paragraph
      current_paragraph.append(f"{start_time}-{end_time} {body}")

    # Handle overlap: Check if the previous segment's body is the same
    if i > 0 and speaker != current_speaker and json_data['segments'][i - 1]['body'] == body:
      current_paragraph.append(f"{start_time}-{end_time} {body}")  # Append to previous speaker
      current_speaker = json_data['segments'][i - 1]['speaker']  # Update speaker

  # Add the last paragraph
  if current_paragraph:
    markdown += f"{current_speaker}: {current_paragraph}\n\n"

  return markdown

# Load JSON data from file
with open("transcript.json", "r") as f:
  transcript = json.load(f)

# Convert to Markdown and print
markdown_transcript = json_to_markdown(transcript)
print(markdown_transcript)
