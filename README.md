# Hindenburg helpers

A collection of tools for modifying Hindenburg projects.

## Hindenburg Editor

A tool for editing Hindenburg projects. See `spec.md`.

## Silence remover

A tool for muting tracks when they're not active.

## whisper-subtools

Modify transcripts created by Whisper to be more human-readable

## xml-merge

Combine the transcripts from two Hindenburg .nhsx files and save them
into a third file. Used to help the user not use edits made into one project
and merge transcription data from an unedited session with it.

## nhsx-to-script

Parse Hindenburg transcripts into a human-readable .md format

## reorder-hindenburg-subdirectories

Meant to help you save space if several projects share the same audio
files.

## Litterointi-työkirja (Transcription Notebook)

Tämä on Google Colab -työkirja (`Litterointi_–_Hindenburg_w_whisper-timestamped.ipynb`), joka on suunniteltu audio-tiedostojen litterointiin Hindenburg-projekteja varten.

### Ominaisuudet

- **Tarkka litterointi:** Käyttää `whisper-timestamped`-kirjastoa ja `openai/whisper-large-v3-turbo`-mallia tuottaakseen tarkkoja, sanakohtaisilla aikaleimoilla varustettuja tekstityksiä.
- **Google Drive -integraatio:** Lukee äänitiedostot Google Driven `whisper/input`-kansiosta ja tallentaa tulokset (`.nhsx`-tiedostot) `whisper/output`-kansioon.
- **Hindenburg-yhteensopivuus:** Muokkaa olemassa olevia `.nhsx`-projektitiedostoja ja lisää niihin tuotetut litteroinnit.
- **Nopeutettu käynnistys:** Hyödyntää Google Drivella olevaa välimuistia (`whisper/cache`), mikä nopeuttaa merkittävästi mallien lataamista toistuvilla ajokerroilla.

### Käyttö

1.  Avaa `Litterointi_–_Hindenburg_w_whisper-timestamped.ipynb` Google Colabissa.
2.  Aseta käsiteltävät äänitiedostot ja Hindenburg-projektisi (`.nhsx`) Google Driven `whisper/input`-kansioon.
3.  Suorita työkirjan solut ohjeiden mukaan.
4.  Valmiit, litteroinnit sisältävät `.nhsx`-tiedostot löytyvät `whisper/output`-kansiosta.
