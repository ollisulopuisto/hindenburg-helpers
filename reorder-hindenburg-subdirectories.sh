#!/bin/zsh

# This script consolidates .wav files from subdirectories into a "Combined_WAVs" directory
# and updates the corresponding .nhsx XML files to reflect the new file locations.

#
# BUGFIX: make sure the wav files are unique before moving them!
# This comment indicates that the following code block addresses a bug where non-unique 
# .wav files were being overwritten during the consolidation process.
#

# Check if exactly one argument (the directory path) is provided.
if [ $# -eq 0 ] ; then
    # If no argument is provided, print an error message and exit.
    echo "Please provide a directory path as an argument."
    exit
fi

# Store the provided directory path in the variable 'mainDir'.
mainDir=$1
# Create the "Combined_WAVs" directory inside 'mainDir', recursively if needed.
mkdir -p "$mainDir/Combined_WAVs"

# Find all directories within 'mainDir' and process each directory.
# The '-print0' option separates directory names with a null character,
# preventing issues with spaces in directory names.
# The 'read -rd '' subdir' part reads the directory names separated by null characters.
find "$mainDir" -type d -print0 | while read -rd '' subdir; do
    # Extract the base name of the current subdirectory and store it in 'subDirBase'.
    subDirBase=$(basename "$subdir")
    
    # Find all .wav files within the current subdirectory and process each file.
    find "$subdir" -name "*.wav" -print0 | while read -rd '' wavFile; do
        # Extract the base name of the current .wav file and store it in 'wavBase'.
        wavBase=$(basename "$wavFile")
        
        # Check if a file with the same name already exists in the "Combined_WAVs" directory.
        if [[ -e "$mainDir/Combined_WAVs/$wavBase" ]]; then
            # If a file with the same name exists, compare their sizes to ensure they are different.
            if [[ $(stat -f%z "$mainDir/Combined_WAVs/$wavBase") -ne $(stat -f%z "$wavFile") ]]; then
                # If the files are different, rename the new file by appending the subdirectory name
                # to avoid overwriting existing files in the "Combined_WAVs" directory.
                mv -- "$wavFile" "$mainDir/Combined_WAVs/${wavBase%.*}_$subDirBase.wav"
            fi 
            # If the files are the same size, the file is skipped (assumed to be a duplicate).
        else
            # If no file with the same name exists, move the file to the "Combined_WAVs" directory.
            mv -- "$wavFile" "$mainDir/Combined_WAVs/"
        fi
    done
done

# At this point, all .wav files should have been moved to the "Combined_WAVs" directory.

# Find all .nhsx files within 'mainDir' and process each file.
find "$mainDir" -name "*.nhsx" -print0 | while read -rd '' xmlFile; do
    # Modify the .nhsx XML file to reflect the new location of the .wav files.
    # It replaces the "Location" attribute value in the "AudioPool" tag with the new directory path.
    # The '#' character is used as a separator in the 'sed' command 
    # because file paths may contain the usual '/' separator.
    sed -i '' -e 's#<AudioPool Path="[^"]*" Location="[^"]*"#<AudioPool Path="'"$mainDir"'/Combined_WAVs" Location="'"$mainDir"'/Combined_WAVs"#g' "$xmlFile"
done
