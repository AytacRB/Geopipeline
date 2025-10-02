from typing import Callable, Optional
from pymongo import InsertOne, UpdateOne
from pymongo.errors import BulkWriteError
from tqdm import tqdm
from bson import ObjectId

from geopipeline.db import get_mongo_collection
from geopipeline.workers import run_in_pool


def ner_pipeline(
    mongo_uri: str,
    db: str,
    source_col: str,
    target_col: str,
    model: str,
    process_func: Callable,
    init_worker: Callable,
    workers: Optional[int] = None,
    chunksize: int = 100,
    batch_size: int = 500,
):
    """
    Orchestrates the NER extraction stage.
    """
    client, source = get_mongo_collection(mongo_uri, db, source_col)
    _, target = get_mongo_collection(mongo_uri, db, target_col)

    total_docs = source.count_documents({})
    docs = source.find({}, {"_id": 1, "body": 1})

    batch = []
    try:
        with tqdm(total=total_docs, desc="NER Processing", unit="doc") as pbar:
            for result in run_in_pool(
                func=process_func,
                data_iter=docs,
                init=init_worker,
                init_args=(model,),
                workers=workers,
                chunksize=chunksize,
            ):
                batch.append(InsertOne(result))
                if len(batch) >= batch_size:
                    target.bulk_write(batch, ordered=False)
                    batch = []
                pbar.update(1)

            if batch:
                target.bulk_write(batch, ordered=False)
    finally:
        client.close()



def geocode_pipeline(
    mongo_uri: str,
    db: str,
    source_col: str,
    cache_db: str,
    nominatim_url: str,
    process_func: Callable,
    rate_limit: float = 0.0,
    workers: Optional[int] = None,
    chunksize: int = 10,
    bulk_size: int = 250,
    resume: bool = False,
    resume_file: str = "./last_id.txt",
):
    """
    Orchestrates the geocoding stage.
    """
    client, col = get_mongo_collection(mongo_uri, db, source_col)

    # Load last processed id
    last_id = None
    if resume:
        try:
            with open(resume_file, "r") as f:
                last_id_str = f.read().strip()
                if last_id_str:
                    last_id = ObjectId(last_id_str)
        except FileNotFoundError:
            pass

    query = {"_id": {"$gt": last_id}} if last_id else {}
    cursor = col.find(query, {"entities": 1}).sort("_id", 1).batch_size(100)

    total_docs = col.count_documents(query)
    bulk_ops = []

    pool_args = ((doc, nominatim_url, rate_limit, cache_db) for doc in cursor)

    try:
        with tqdm(total=total_docs, desc="Geocoding", unit="doc") as pbar:
            for res in run_in_pool(
                func=process_func,
                data_iter=pool_args,
                workers=workers,
                chunksize=chunksize,
            ):
                bulk_ops.append(
                    UpdateOne({"_id": res["_id"]}, {"$set": {"countries": res["countries"]}})
                )

                if len(bulk_ops) >= bulk_size:
                    try:
                        col.bulk_write(bulk_ops, ordered=False)
                    except BulkWriteError as bwe:
                        print("Bulk write error:", bwe.details)
                    bulk_ops = []

                # Save progress
                if resume:
                    with open(resume_file, "w") as f:
                        f.write(str(res["_id"]))

                pbar.update(1)

        if bulk_ops:
            try:
                col.bulk_write(bulk_ops, ordered=False)
            except BulkWriteError as bwe:
                print("Bulk write error:", bwe.details)

    except KeyboardInterrupt:
        print("Interrupted by user. Progress saved.")
    finally:
        client.close()
        print("Geocoding finished or stopped.")
