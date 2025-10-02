# GeoPipeline

A lightweight **NER + Geocoding pipeline** for extracting geographic entities from text, resolving them with [spaCy](https://spacy.io/) and [Nominatim](https://nominatim.org/), and storing results in MongoDB.

Features:
- Named Entity Recognition (**NER**) using spaCy
- Geocoding of extracted entities with **Nominatim**
- Caching of geocoded entities in SQLite
- Parallelized processing with worker pools
- Resume mode to continue from the last processed record
- MongoDB integration for input/output collections

---

## How to:

- Step 1) Make sure you have a MongoDB instance and a Nominatim instance running
- Step 2) Inside of settings.yml make sure the arguments are pointing to the correct ports (Default: MongoDB on :27017   and Nominatim on :8080)
- Step 3) Run:
  - Option a) Run using CLI
    - geopipeline-ner --db *yourDB* --source-col *yourCol* --target-col *yourTargetCol*
    - geopipeline-geocode *yourDB* --source-col *yourCol* --target-col *yourTargetCol* --cache-db *yourSQLitecache*

  - Option b) Run using preconfigured settings.yml
    - geopipeline-ner --config settings.yml
    - geopipeline-geocode --config settings.yml

Geocoding process uses --resume flag per default for pause/resume feature
