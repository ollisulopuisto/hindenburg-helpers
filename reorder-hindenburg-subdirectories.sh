#!/bin/zsh

#
# BUGFIX: make sure the wav files are unique before moving them!
#

if [ $# -eq 0 ] ; then
    echo "Please provide a directory path as an argument."
    exit
fi

mainDir=$1
mkdir -p "$mainDir/Combined_WAVs"

find "$mainDir" -type d -print0 | while read -rd '' subdir; do
    subDirBase=$(basename "$subdir")
    
    find "$subdir" -name "*.wav" -print0 | while read -rd '' wavFile; do
        wavBase=$(basename "$wavFile")
        
        if [[ -e "$mainDir/Combined_WAVs/$wavBase" ]]; then
            if [[ $(stat -f%z "$mainDir/Combined_WAVs/$wavBase") -ne $(stat -f%z "$wavFile") ]]; then
                mv -- "$wavFile" "$mainDir/Combined_WAVs/${wavBase%.*}_$subDirBase.wav"
            fi
        else
            mv -- "$wavFile" "$mainDir/Combined_WAVs/"
        fi
    done
done

# All .wav files should be moved by now. Modify XML .nhsx files.
find "$mainDir" -name "*.nhsx" -print0 | while read -rd '' xmlFile; do
    # Replace Location attribute value in AudioPool tag with new directory.
    # Using '#' as separator because file paths contains '/'.
    sed -i '' -e 's#<AudioPool Path="[^"]*" Location="[^"]*"#<AudioPool Path="'"$mainDir"'/Combined_WAVs" Location="'"$mainDir"'/Combined_WAVs"#g' "$xmlFile"
done
