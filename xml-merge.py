import xml.etree.ElementTree as ET
import sys

def parse_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return tree, root

def find_file_element(root, name):
    for audio_file in root.findall('.//File'):
        if audio_file.attrib.get('Name') == name:
            return audio_file
    return None

def merge_transcriptions(file_a_root, file_b_root):
    for file_a in file_a_root.findall('.//File'):
        file_b = find_file_element(file_b_root, file_a.attrib.get('Name'))
        if file_b is not None:
            trans_a = file_a.find('Transcription')
            trans_b = file_b.find('Transcription')
            if trans_a is not None:
                if trans_b is not None:
                    file_b.remove(trans_b)
                file_b.append(trans_a)

def main(file_a_path, file_b_path, file_c_path):
    # Parse input files
    tree_a, root_a = parse_file(file_a_path)
    tree_b, root_b = parse_file(file_b_path)
    
    # Merge transcriptions
    merge_transcriptions(root_a, root_b)
    
    # Save the result to file C
    tree_b.write(file_c_path, encoding='utf-8', xml_declaration=True)
    print(f'Merged file saved as: {file_c_path}')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_xml.py <file_a.xml> <file_b.xml> <output_file_c.xml>")
        sys.exit(1)
    
    file_a_path = sys.argv[1]
    file_b_path = sys.argv[2]
    file_c_path = sys.argv[3]
    
    main(file_a_path, file_b_path, file_c_path)
