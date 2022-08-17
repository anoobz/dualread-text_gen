import random

from dotenv import load_dotenv

from analyze import analyze_generation, analyze_translation
from generate import filter_sentences, generate_sentences

from mongodb import MongoDatabase
from translate_client import Translater

load_dotenv()


if __name__ == "__main__":
    # Generation parameters
    target_language = "zh-CN"
    sentence_delimiter = "。"
    template_start = 0
    template_end = template_start + 10
    start_ratio = 0.1
    end_ratio = 1
    char_count_threshold = 2
    shuffle = True

    # Input and output files
    template_version = 0
    templates_file_name = f"templates/v{template_version}.json"
    generation_file_name = (
        f"output_files/gen "
        + f"v{template_version} "
        + f"t{template_start}-{template_end} "
        + f"r{start_ratio}-{end_ratio} "
        + f"c{char_count_threshold}.txt"
    )
    translation_file_name = (
        f"output_files/tran "
        + f"v{template_version} "
        + f"t{template_start}-{template_end} "
        + f"r{start_ratio}-{end_ratio} "
        + f"c{char_count_threshold}.txt"
    )

    mongo_db = MongoDatabase()
    translate_client = Translater(mongo_db, target_language)

    generated_sentences = generate_sentences(
        templates_file_name, template_start, template_end, start_ratio, end_ratio
    )
    with open(generation_file_name, "w") as f:
        f.write("\n".join(generated_sentences))

    translated_sentences = translate_client.translate(generated_sentences)

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
