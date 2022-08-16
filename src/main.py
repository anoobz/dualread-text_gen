import random

from dotenv import load_dotenv

from analyze import analyze_generation, analyze_translation
from generate import filter_sentences, generate_sentences

from mongodb import MongoDatabase
from translate_client import TranslateClient

load_dotenv()


if __name__ == "__main__":
    # Input and output files
    templates_file_name = "templates.json"
    generation_file_name = "output_files/generated_sentences.txt"
    translation_file_name = "output_files/filtered_translated_sentences.txt"

    # Generation parameters
    source_language = "en"
    target_language = "zh-CN"
    template_start = 0
    template_end = template_start + 10
    start_ratio = 0.1
    end_ratio = 1
    char_count_threshold = 0
    sentence_delimiter = "。"
    shuffle = True

    mongo_client = MongoDatabase()
    translate_client = TranslateClient()

    generated_sentences = generate_sentences(
        templates_file_name, template_start, template_end, start_ratio, end_ratio
    )
    with open(generation_file_name, "w") as f:
        f.write("\n".join(generated_sentences))

    translated_sentences: list[str] = []
    for sentence in generated_sentences:
        translation = mongo_client.find_translation(
            sentence, source_language, target_language
        )
        if translation:
            translated_sentences.append(translation["output"])
        else:
            translation = translate_client.translate(
                sentence, source_language, target_language
            )
            mongo_client.insert_translation(
                sentence, translation, source_language, target_language
            )
            translated_sentences.append(translation)

    filtered_sentences = filter_sentences(
        "\n".join(translated_sentences), char_count_threshold, sentence_delimiter
    )

    if shuffle:
        random.shuffle(filtered_sentences)

    print(f"Generated {len(filtered_sentences)} sentences")
    translations = "\n".join(filtered_sentences)
    with open(translation_file_name, "w") as f:
        f.write(translations)

    analyze_generation(" ".join(generated_sentences))
    analyze_translation(translations)
