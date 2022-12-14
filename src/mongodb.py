import os
from typing import Any, Optional
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection


class MongoDatabase:
    coll: Collection

    def __init__(self) -> None:

        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "27017")
        db_name = os.getenv("DB_NAME", "text_gen")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")

        db_uri = f"mongodb://{username}:{password}@{host}:{port}/"

        client = MongoClient(db_uri)

        db = client.get_database(db_name)

        self.coll = db.get_collection("translation")
        self.coll.create_index(
            [
                ("input", DESCENDING),
                ("source_language", DESCENDING),
                ("target_language", DESCENDING),
            ]
        )

    def insert_translation(
        self, input: str, output: str, source_language: str, target_language: str
    ):
        self.coll.insert_one(
            {
                "input": input,
                "output": output,
                "source_language": source_language,
                "target_language": target_language,
            }
        )

    def find_translation(
        self, input: str, source_language: str, target_language: str
    ) -> Optional[dict[str, Any]]:
        trans = self.coll.find_one(
            {
                "input": input,
                "source_language": source_language,
                "target_language": target_language,
            }
        )

        return trans

    def delete_all_translation(self):
        self.coll.delete_many({})
