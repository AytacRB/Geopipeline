import argparse
from geopipeline import geocode, pipeline


def main():
    parser = argparse.ArgumentParser(description="Geocoding pipeline")
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    parser.add_argument("--db", default="mediaTracker")
    parser.add_argument("--source-col", default="media_en_gpes")
    parser.add_argument("--cache-db", default="./entity_geo_cache.sqlite")
    parser.add_argument("--nominatim-url", default="http://localhost:8080")
    parser.add_argument("--bulk-size", type=int, default=250)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--rate-limit", type=float, default=0.0)
    parser.add_argument("--chunksize", type=int, default=10)
    parser.add_argument("--resume", action="store_true", help="Resume from last processed doc")
    parser.add_argument("--resume-file", default="./last_id.txt")
    args = parser.parse_args()

    pipeline.geocode_pipeline(
        mongo_uri=args.mongo_uri,
        db=args.db,
        source_col=args.source_col,
        cache_db=args.cache_db,
        nominatim_url=args.nominatim_url,
        process_func=geocode.process_doc,
        rate_limit=args.rate_limit,
        workers=args.workers,
        chunksize=args.chunksize,
        bulk_size=args.bulk_size,
        resume=args.resume,
        resume_file=args.resume_file,
    )
