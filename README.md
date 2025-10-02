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

## Project Structure


geopipeline/
├── cli/                
│   ├── geocode_cli.py  # CLI for geocoding
│   └── ner_cli.py      # CLI for NER
├── db.py               # MongoDB + SQLite cache helpers
├── geocode.py          # Geocoding logic
├── ner.py              # NER logic
├── pipeline.py         # Combined NER + geocode pipeline
├── workers.py          # Parallel processing helpers
├── config.py           
scripts/                # Scripts for Nominatim / docker-compose
requirements.txt        
pyproject.toml 
settings.yml            
