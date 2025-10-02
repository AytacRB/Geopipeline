import requests, time
from typing import Dict, Any, Optional, List
from geopipeline.db import GeoCache

# Nominatim Query 
def query_nominatim(nominatim_url: str, entity: str, session: requests.Session) -> List[Dict[str, Any]]:
    params = {"q": entity, "format": "json", "addressdetails": 1, "limit": 50}
    resp = session.get(nominatim_url.rstrip('/') + "/search", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def filter_country(results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for r in results:
        if r.get("addresstype") == "country":
            return {
                "country": r.get("name"),
                "lat": r.get("lat"),
                "lon": r.get("lon"),
                "osm_type": r.get("osm_type"),
                "osm_id": r.get("osm_id"),
                "match_type": r.get("type"),
            }
    return None

def process_doc(args) -> Dict[str, Any]:
    doc, nominatim_url, rate_limit, cache_path = args
    entities = doc.get("entities", [])
    session = requests.Session()
    cache = GeoCache(cache_path)

    countries = []
    for entity in entities:
        entity_key = entity.strip()
        if not entity_key:
            continue
        # Check cache    
        cached = cache.get(entity_key)
        if cached is not None:
            country_obj = cached
        else:
            try: # query Nominatim
                results = query_nominatim(nominatim_url, entity_key, session)
                country_obj = filter_country(results)
                cache.set(entity_key, country_obj)
                if rate_limit > 0:
                    time.sleep(rate_limit)
            except Exception:
                country_obj = None
                cache.set(entity_key, None)  # negative caching 

        if country_obj:
            countries.append(country_obj)

    # Deduplicate
    unique = {c["country"]: c for c in countries if c.get("country")}
    return {"_id": doc["_id"], "countries": list(unique.values())}
