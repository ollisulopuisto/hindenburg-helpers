import argparse
import sys
from lxml import etree
from collections import defaultdict
import os

def time_to_seconds(time_str):
    """Muuntaa Hindenburgin aikaformaatin (esim. 01:02:03.456 tai 123.45) sekunneiksi."""
    if ':' in time_str:
        parts = time_str.split(':')
        seconds = float(parts[-1])
        minutes = int(parts[-2]) if len(parts) > 1 else 0
        hours = int(parts[-3]) if len(parts) > 2 else 0
        return hours * 3600 + minutes * 60 + seconds
    else:
        return float(time_str)

def seconds_to_time(seconds):
    """Muuntaa sekunnit Hindenburgin aikaformaattiin (SS.ms)."""
    return f"{seconds:.3f}"

def merge_intervals(intervals):
    """Yhdistää päällekkäiset tai peräkkäiset aikaikkunat."""
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    
    merged = [intervals[0]]
    for current_start, current_end in intervals[1:]:
        last_start, last_end = merged[-1]
        
        # Pieni toleranssi (esim. 10 ms) pienten puhekatkojen yhdistämiseksi
        if current_start <= last_end + 0.01:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))
            
    return merged

def get_speech_intervals(tree):
    """
    Hakee kaikkien äänitiedostojen puheintervallit transkriptioista.
    Palauttaa sanakirjan: {file_id: [(start, end), ...]}
    """
    print("Vaihe 1/5: Haetaan puhejaksoja transkriptioista...")
    speech_intervals_by_file = defaultdict(list)
    audio_pool = tree.find('AudioPool')
    if audio_pool is None:
        return speech_intervals_by_file

    for file_elem in audio_pool.findall('File'):
        file_id = file_elem.get('Id')
        transcription = file_elem.find('Transcription')
        if transcription is not None:
            intervals = []
            for word in transcription.findall('.//w'):
                start = float(word.get('s'))
                length = float(word.get('l'))
                intervals.append((start, start + length))
            
            # Yhdistetään peräkkäiset sanat yhtenäisiksi puhejaksoiksi
            speech_intervals_by_file[file_id] = merge_intervals(intervals)
    
    print(f"-> Löydetty puhetta {len(speech_intervals_by_file)} tiedostosta.")
    return speech_intervals_by_file

def map_intervals_to_timeline(tree, speech_intervals_by_file):
    """
    Muuntaa tiedostokohtaiset puheajat projektin absoluuttiselle aikajanalle.
    Palauttaa sanakirjan: {track_name: [(start, end), ...]}
    """
    print("Vaihe 2/5: Muunnetaan puheajat projektin aikajanalle...")
    speech_on_timeline = defaultdict(list)
    tracks = tree.find('Tracks')
    if tracks is None:
        return speech_on_timeline

    for track in tracks.findall('Track'):
        track_name = track.get('Name')
        track_intervals = []
        for region in track.findall('Region'):
            ref_id = region.get('Ref')
            if ref_id in speech_intervals_by_file:
                region_start = time_to_seconds(region.get('Start', '0.0'))
                region_offset = time_to_seconds(region.get('Offset', '0.0'))
                
                for file_start, file_end in speech_intervals_by_file[ref_id]:
                    # Varmistetaan, että puhejakso osuu tämän regionin sisään
                    if file_start >= region_offset and file_end <= region_offset + time_to_seconds(region.get('Length')):
                        timeline_start = region_start + (file_start - region_offset)
                        timeline_end = region_start + (file_end - region_offset)
                        track_intervals.append((timeline_start, timeline_end))

        speech_on_timeline[track_name] = merge_intervals(track_intervals)
        print(f"-> Käsitelty raita: '{track_name}'")
    return speech_on_timeline

def calculate_mute_intervals(speech_on_timeline):
    """
    Laskee kullekin raidalle ne aikavälit, jotka tulee vaimentaa.
    Vaimennus tapahtuu, kun joku toinen puhuu, mutta kyseinen raita on hiljaa.
    """
    print("Vaihe 3/5: Lasketaan vaimennettavia jaksoja...")
    mute_intervals = defaultdict(list)
    all_track_names = list(speech_on_timeline.keys())

    for target_track_name in all_track_names:
        # 1. Kerää kaikkien muiden puhujien puheajat yhteen
        others_speech = []
        for other_track_name in all_track_names:
            if other_track_name != target_track_name:
                others_speech.extend(speech_on_timeline[other_track_name])
        
        merged_others_speech = merge_intervals(others_speech)
        
        # 2. Hae kohderaidan omat puheajat
        target_speech = speech_on_timeline.get(target_track_name, [])
        
        # 3. Etsi jaksot, joissa muut puhuvat, mutta kohderaita EI puhu
        for other_start, other_end in merged_others_speech:
            current_interval_start = other_start
            
            for target_start, target_end in target_speech:
                if current_interval_start < target_start and other_end > current_interval_start:
                    mute_end = min(other_end, target_start)
                    if mute_end > current_interval_start:
                        mute_intervals[target_track_name].append((current_interval_start, mute_end))
                
                if current_interval_start < target_end:
                     current_interval_start = max(current_interval_start, target_end)

            if current_interval_start < other_end:
                 mute_intervals[target_track_name].append((current_interval_start, other_end))
    
    for track_name, intervals in mute_intervals.items():
         print(f"-> Raidalle '{track_name}' laskettu {len(intervals)} vaimennusjaksoa.")
         
    return mute_intervals

def apply_muting(tree, mute_intervals):
    """
    Muokkaa XML-puuta: pilkkoo regionit ja lisää Muted="True" -määritteet.
    """
    print("Vaihe 4/5: Muokataan raitoja ja lisätään vaimennuksia...")
    tracks_elem = tree.find('Tracks')
    if tracks_elem is None:
        return

    for track_name, mutes in mute_intervals.items():
        track_elem = tracks_elem.find(f"Track[@Name='{track_name}']")
        if track_elem is None or not mutes:
            continue

        original_regions = list(track_elem.findall('Region'))
        new_regions = []
        
        for region in original_regions:
            region_start = time_to_seconds(region.get('Start', '0.0'))
            region_length = time_to_seconds(region.get('Length'))
            region_end = region_start + region_length
            region_offset = time_to_seconds(region.get('Offset', '0.0'))

            cuts = {region_start, region_end}
            for mute_start, mute_end in mutes:
                if mute_start > region_start and mute_start < region_end:
                    cuts.add(mute_start)
                if mute_end > region_start and mute_end < region_end:
                    cuts.add(mute_end)
            
            sorted_cuts = sorted(list(cuts))
            
            for i in range(len(sorted_cuts) - 1):
                cut_start = sorted_cuts[i]
                cut_end = sorted_cuts[i+1]
                
                new_region = etree.Element("Region", attrib=region.attrib)
                
                new_start_time = cut_start
                new_length_time = cut_end - cut_start
                new_offset_time = region_offset + (cut_start - region_start)

                new_region.set('Start', seconds_to_time(new_start_time))
                new_region.set('Length', seconds_to_time(new_length_time))
                new_region.set('Offset', seconds_to_time(new_offset_time))

                # Tarkista, pitääkö tämä uusi pätkä vaimentaa
                is_muted = False
                mid_point = cut_start + new_length_time / 2
                for mute_start, mute_end in mutes:
                    if mid_point >= mute_start and mid_point < mute_end:
                        is_muted = True
                        break
                
                if is_muted:
                    new_region.set('Muted', 'True')
                elif 'Muted' in new_region.attrib:
                    del new_region.attrib['Muted']

                new_regions.append(new_region)

        # Korvataan vanhat regionit uusilla
        for region in original_regions:
            track_elem.remove(region)
        for new_region in new_regions:
            track_elem.append(new_region)
        print(f"-> Raita '{track_name}' päivitetty {len(new_regions)} leikkeellä.")


def main():
    parser = argparse.ArgumentParser(
        description='Vaimentaa automaattisesti hiljaiset osuudet Hindenburg .nhsx -tiedostosta.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('input_file', help='Polku alkuperäiseen .nhsx-tiedostoon.')
    parser.add_argument('output_file', help='Polku, johon muokattu .nhsx-tiedosto tallennetaan.')
    args = parser.parse_args()

    input_path = os.path.expanduser(args.input_file)
    output_path = os.path.expanduser(args.output_file)

    if not os.path.exists(input_path):
        print(f"Virhe: Tiedostoa ei löytynyt: {input_path}")
        sys.exit(1)

    try:
        # Käytetään parseria, joka säilyttää kommentit ja XML-deklaraation
        parser = etree.XMLParser(remove_blank_text=False, strip_cdata=False)
        tree = etree.parse(input_path, parser)
        
        speech_intervals = get_speech_intervals(tree)
        speech_on_timeline = map_intervals_to_timeline(tree, speech_intervals)
        mute_intervals = calculate_mute_intervals(speech_on_timeline)
        apply_muting(tree, mute_intervals)

        print(f"\nVaihe 5/5: Kirjoitetaan muokattu tiedosto...")
        # Kirjoitetaan tiedosto säilyttäen alkuperäinen muotoilu mahdollisimman hyvin
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        
        print(f"Valmis! Muokattu tiedosto on tallennettu sijaintiin:\n{output_path}")

    except Exception as e:
        print(f"\nKäsittelyssä tapahtui odottamaton virhe: {e}")
        print("Varmista, että tiedosto on validi Hindenburg (.nhsx) -tiedosto.")
        sys.exit(1)


if __name__ == '__main__':
    main()