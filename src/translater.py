import os, json
from typing import Any
from google.cloud.translate import TranslationServiceClient
from google.cloud.translate_v3.types.translation_service import Translation

from mongodb import MongoDatabase


class Translater:
    def __init__(
        self,
        mongo_db: MongoDatabase,
        target_language_code: str,
        source_language_code: str = "en",
    ):
        self.keys: dict[str, Any] = json.loads(os.getenv("GOOGLE_API_KEYS", "{}"))
        self.google_client = TranslationServiceClient.from_service_account_info(
            self.keys
        )
        self.mongo_db = mongo_db
        self.target_language_code = target_language_code
        self.source_language_code = source_language_code

    def fetch_translations(self, input: str) -> str:
        project_id = self.keys.get("project_id", "")
        location = "global"
        res = self.google_client.translate_text(
            request={
                "parent": f"projects/{project_id}/locations/{location}",
                "contents": [input],
                "mime_type": "text/plain",
                "source_language_code": self.source_language_code,
                "target_language_code": self.target_language_code,
            }
        )
        if not res:
            raise Exception("could not fetch translation")

        return Translation.to_dict(res.translations[0])[  # type: ignore
            "translated_text"
        ]

    def translate(self, generated_sentences: list[str]) -> list[str]:
        translated_sentences: list[str] = []
        for sentence in generated_sentences:
            translation = self.mongo_db.find_translation(
                sentence, self.source_language_code, self.target_language_code
            )
            if translation:
                translated_sentences.append(translation["output"])
            else:
                translation = self.fetch_translations(sentence)
                self.mongo_db.insert_translation(
                    sentence,
                    translation,
                    self.source_language_code,
                    self.target_language_code,
                )
                translated_sentences.append(translation)

        return translated_sentences
