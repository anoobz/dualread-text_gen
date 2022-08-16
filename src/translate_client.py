import os, json
from typing import Any
from google.cloud.translate import TranslationServiceClient
from google.cloud.translate_v3.types.translation_service import Translation


class TranslateClient:
    def __init__(self):
        self.keys: dict[str, Any] = json.loads(os.getenv("GOOGLE_API_KEYS", "{}"))
        self.client = TranslationServiceClient.from_service_account_info(self.keys)

    def translate(
        self, input: str, source_language_code: str, target_language_code: str
    ) -> str:
        project_id = self.keys.get("project_id", "")
        location = "global"
        res = self.client.translate_text(
            request={
                "parent": f"projects/{project_id}/locations/{location}",
                "contents": [input],
                "mime_type": "text/plain",
                "source_language_code": source_language_code,
                "target_language_code": target_language_code,
            }
        )
        if not res:
            raise Exception("could not fetch translation")

        return Translation.to_dict(res.translations[0])[  # type: ignore
            "translated_text"
        ]
