# Hindenburg helpers

> **Lähes kaikki tästä on siirtynyt.** Istuntoformaattia jäsennetään yhdessä
> paikassa yhdellä tavalla: [`ollisulopuisto/podcast`](https://github.com/ollisulopuisto/podcast)in
> `podcast-magic` lukee ja kirjoittaa `.nhsx`:ää yhdellä testatulla
> jäsentimellä, ja istunnon voi renderöidä WAViksi ilman Hindenburgia.
>
> | mitä täällä oli | minne se meni |
> |---|---|
> | `xml-merge.py` | `podcast-magic`in **Litteroinnin siirto** -moduuli |
> | `nhsx-to-script.py` | `podcast-magic`in **Käsikirjoitus**-moduuli |
> | `strip-silence.py`, `vaienna_hiljaiset_kohdat_*.py`, molemmat muistikirjat | poistettu — `podcast-magic`in litterointi ja vaimennus tekevät saman työn mitattuna |
> | `hindenburg-editor.py` | poistettu — ei koskaan lukenut yhtäkään istuntoa (ks. git-historia) |
> | `spec.md` | `podcast-magic/docs/hindenburg-session-spec.md` |
> | `MOVE.md`, `AGENT.md` | poistettu — suoritettu, vanhentunut |

## Jäljellä

* `reorder-hindenburg-subdirectories.sh` — säästää levytilaa kun projektit
  jakavat äänitiedostoja. Ei lue istuntoformaattia eikä käsittele ääntä:
  hakemistojen siivousta, ei istuntoformaattia.
* `json-to-text.py` — Whisperin JSON-litterointi tekstinä. Poista, jos
  Whisperin JSONia ei enää synny.
