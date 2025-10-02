from typing import Dict, Any, Optional, List
from collections import Counter
import spacy

# Global model (loaded once per worker)
_nlp: Optional[spacy.language.Language] = None


def init_worker(model_name: str) -> None:
    global _nlp
    _nlp = spacy.load(
        model_name,
        disable=["tok2vec", "tagger", "parser",
                 "attribute_ruler", "lemmatizer", "morphologizer"]
    )
    return None

def extract_gpes(text: str) -> List[str]:
    """
    Extract GPE entities from text using spaCy.
    """
    global _nlp
    if not text:
        return []

    doc = _nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]


def process_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a MongoDB document and extract GPE entities.
    Returns a dict with _id, entities, and entity_counts.
    """
    text = doc.get("body", "")
    gpes = extract_gpes(text)

    if not gpes:
        return {"_id": doc["_id"], "entities": [], "entity_counts": {}}

    counts = dict(Counter(gpes))
    return {
        "_id": doc["_id"],
        "entities": list(counts.keys()),
        "entity_counts": counts,
    }
