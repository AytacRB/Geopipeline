import argparse
from geopipeline import ner, pipeline


def main():
    parser = argparse.ArgumentParser(description="NER extraction pipeline")
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    parser.add_argument("--db", default="mediaTracker")
    parser.add_argument("--source-col", default="media_en")
    parser.add_argument("--target-col", default="media_en_gpes")
    parser.add_argument("--model", default="en_core_web_md")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--chunksize", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()

    pipeline.ner_pipeline(
        mongo_uri=args.mongo_uri,
        db=args.db,
        source_col=args.source_col,
        target_col=args.target_col,
        model=args.model,
        process_func=ner.process_doc,
        init_worker=ner.init_worker,
        workers=args.workers,
        chunksize=args.chunksize,
        batch_size=args.batch_size,
    )
