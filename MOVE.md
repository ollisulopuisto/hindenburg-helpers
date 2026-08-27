# Pitäisikö nämä siirtää `ollisulopuisto/podcast`iin?

Kyllä — mutta ei repositoriona. Näistä seitsemästä työkalusta **kolme on jo
siellä paremmassa muodossa**, yksi ei toimi lainkaan, ja kaksi kannattaa
siirtää. Alla mikä on mitäkin ja miksi.

Kirjoitettu 2026-08-27. Tämä on suositus eikä tehty työ: mitään ei ole vielä
siirretty.

## Yhteenveto

| tiedosto | mitä sille kuuluu tehdä |
|---|---|
| `strip-silence.py`, `vaienna_hiljaiset_kohdat_*` | **poista** — `podcast-magic`in `silence/` on sama työ mitattuna |
| `Litterointi_–_Hindenburg_w_whisper-timestamped.ipynb` | **poista** — `podcast-magic`in `transcribe/` on sama työ GPU:lla |
| `hindenburg-editor.py` | **poista** — ei ole koskaan toiminut, ks. alla |
| `nhsx-to-script.py` | **siirrä** moduuliksi `podcast-magic`iin |
| `xml-merge.py` | **siirrä** moduuliksi `podcast-magic`iin |
| `json-to-text.py` | jätä tänne, tai poista jos Whisperin JSONia ei enää synny |
| `reorder-hindenburg-subdirectories.sh` | **jätä tänne** — levyn siivousta, ei istuntoformaattia |

## Miksi: sama formaatti on jäsennetty kuusi kertaa

`time_to_seconds` — funktio joka lukee Hindenburgin aikamuodon — on
kirjoitettu **kuudesti**, viisi kertaa tässä repositoriossa:

    hindenburg-helpers/hindenburg-editor.py
    hindenburg-helpers/nhsx-to-script.py
    hindenburg-helpers/strip-silence.py
    hindenburg-helpers/vaienna_hiljaiset_kohdat_(hindenburg).py
    hindenburg-helpers/Vaienna_hiljaiset_kohdat_(Hindenburg).ipynb
    podcast/apps/podcast-magic/src/podcastmagic/nhsx/read.py

Ja ne ovat eri mieltä. `<Region>`in `Muted`ista on kaksi eri totuutta samassa
hakemistossa: muistikirja kirjoittaa `'True'`, `hindenburg-editor.py` lukee
`== '1'`. Kumpikaan ei ole väärässä siitä mitä *se* kirjoittaa, mutta ne
eivät lue toistensa tuotosta.

Tämä on täsmälleen se vika, jota vastaan `podcast` on olemassa. Sen
`CONTRIBUTING.md` kertoo saman tapahtuneen ääniketjulle: kolme kopiota
ajautui erilleen, ja automixer oli neljä mitattua äänikorjausta jäljessä
ennen kuin joku mittasi.

## `hindenburg-editor.py` ei ole keskeneräinen vaan rikki

Se ei ole «stubi jota ei ole vielä viimeistelty». Se ei ole koskaan lukenut
yhtäkään Hindenburgin istuntoa. Kolme mitattua vikaa:

**1. Se etsii elementtiä jota ei ole.** Rivi 78 hakee `.//AudioFile`;
tiedostossa lukee `<File>`. Oikeaan istuntoon ajettuna:

    .//AudioFile  (mitä hindenburg-editor.py etsii): 0
    .//File       (mitä tiedostossa on):             2

**2. Se kaatuu siihen aikamuotoon jota Hindenburg käyttää.**
`time_to_seconds` jakaa merkkijonon sekä `:`- että `.`-merkeistä ja odottaa
kolmea osaa. Hindenburg kirjoittaa yleensä pelkkiä sekunteja:

    '12.500'    -> IndexError
    '0.000'     -> IndexError
    '34:46.400' -> 125560

**3. Ja kolmas rivi on väärin myös silloin kun se ei kaadu.** Saman
repositorion `spec.md` sanoo että `34:46.400` on **2086,4** sekuntia. Tuo
funktio antaa 125560 — kertoimet ovat 60× pielessä, koska millisekunnit
päätyvät sekuntien paikalle. Toteutus on eri mieltä oman speksinsä kanssa,
eikä sitä ole koskaan ajettu tiedostoon jossa se olisi näkynyt.

`spec.md` itsessään on hyvä ja kannattaa säilyttää — se on `podcast-magic`in
`nhsx/read.py`:n esi-isä ja kuvaa datamallin oikein. Se on toteutus, joka ei
vastaa sitä.

## Mitä siirto antaisi: `nhsx/` on jo se mitä nämä yrittivät olla

`podcast-magic`in `nhsx/read.py` on sama jäsennin, mutta kirjoitettuna
oikeita tiedostoja vasten:

* **nimiavaruudet.** Elementit haetaan paikallisnimellä, koska Hindenburgin
  viemät tiedostot ovat joskus nimiavaruudessa ja joskus eivät. Tämän
  repositorion `findall('.//File')` löytää nimiavaruudellisesta istunnosta
  nolla tiedostoa.
* **molemmat aikamuodot**, eikä kaadu kummastakaan.
* **äänipoolin paikannus levyltä.** `Path` on istunnoissa milloin
  absoluuttinen, milloin suhteellinen, milloin pelkkä nimi; `locate` kokeilee
  kaikki kolme ennen kuin lähtee rekursioon.
* **testit.** Jäsentimellä on niitä, näillä skripteillä ei ole yhtään.

Ja päälle se, mitä täällä ei ole lainkaan: `nhsx/mix.py` ja `nhsx/render.py`
soittavat ja renderöivät istunnon, `nhsx/prospect.py` kertoo mitä
formaatissa on, `nhsx/verify.py` etsii litteroinnista sen mikä rikkoo
käsikirjoitusnäkymän aikaindeksin.

## Ristiinpölytys toiseen suuntaan

Kaksi työkalua, joita `podcast`issa **ei ole** ja jotka ovat oikeasti
hyödyllisiä:

**`xml-merge.py`** siirtää litteroinnin istunnosta toiseen. Se ratkaisee
todellisen ongelman: leikkaus on tehty käsin editoituun istuntoon, ja
litterointi on leikkaamattomassa. Ilman tätä toisen niistä tekee uudestaan.
`podcast-magic`issa se olisi moduuli neljällä palasella (merkintä
`modules.py`:hyn, `APIRouter`, `mod_*.js`) ja jäsennin tulisi valmiina.

Yksi asia kannattaa korjata siirron yhteydessä: nykyinen versio korvaa
`<Transcription>`in kohdetiedostossa katsomatta, oliko siellä jo jotain, eikä
tarkista osuvatko tiedostojen kestot toisiinsa. Väärään istuntoon ajettuna se
tuottaa kelvollisen tiedoston jonka sanat ovat väärissä kohdissa —
täsmälleen sen luokan hiljainen vika, jota `podcast`in `CLAUDE.md` varoo.

**`nhsx-to-script.py`** tekee litteroinnista luettavan `.md`:n. Sama
huomautus: `nhsx/read.py` osaa sanat ja niiden ajat jo, joten siirretty
versio on lyhyempi kuin nykyinen.

## Mitä ei kannata siirtää

`reorder-hindenburg-subdirectories.sh` säästää levytilaa kun projektit
jakavat äänitiedostoja. Se ei lue istuntoformaattia eikä käsittele ääntä —
se on hakemistojen siivousta. Se kuuluu tänne.

## Ehdotettu järjestys

1. Siirrä `xml-merge` moduuliksi `podcast-magic`iin, `nhsx/read.py`:n päälle,
   testeineen. Se on niistä kahdesta arvokkaampi ja se, jossa hiljainen vika
   maksaa eniten.
2. Siirrä `nhsx-to-script` samalla tavalla.
3. Poista siirretyt ja korvatut täältä, ja jätä `README.md`:hyn rivi joka
   kertoo mihin ne menivät.
4. `spec.md` seuraa mukana `podcast-magic`in dokumentaatioon; `hindenburg-editor.py`
   ei.

Tämän jälkeen tähän repositorioon jää yksi shell-skripti ja historia — ja
istuntoformaattia jäsennetään yhdessä paikassa yhdellä tavalla, sen
sijaan että kuudessa paikassa kuudella.
