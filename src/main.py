import os
import random
from datetime import datetime
from dotenv import load_dotenv

from analyze import analyze_generation, analyze_translation
from generate import filter_sentences, generate_sentences, reduce_sentences

from mongodb import MongoDatabase
from translater import Translater

load_dotenv()


if __name__ == "__main__":
    # Generation parameters
    target_language = "zh-CN"
    sentence_delimiter = "。"
    template_start = 0
    template_end = template_start + 10
    start_ratio = 0.05
    end_ratio = 0.5
    char_count_threshold = 3
    shuffle = True

    # Input and output files
    template_version = "hsk1_0"
    templates_file_name = f"templates/{template_version}.json"

    output_path = f"./output_files/{datetime.now().date()}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    generation_file_name = (
        f"{output_path}/gen "
        + f"{template_version} "
        + f"t{template_start}-{template_end} "
        + f"r{start_ratio}-{end_ratio} "
        + f"c{char_count_threshold}.txt"
    )
    translation_file_name = (
        f"{output_path}/tran "
        + f"{template_version} "
        + f"t{template_start}-{template_end} "
        + f"r{start_ratio}-{end_ratio} "
        + f"c{char_count_threshold}.txt"
    )

    mongo_db = MongoDatabase()
    translate_client = Translater(mongo_db, target_language)

    generated_sentences = generate_sentences(
        templates_file_name,
        template_start,
        template_end,
    )
    analyze_generation(" ".join(generated_sentences))
    with open(generation_file_name, "w") as f:
        f.write("\n".join(generated_sentences))

    translated_sentences = translate_client.translate(generated_sentences)

    filtered_sentences = filter_sentences(
        "\n".join(translated_sentences), char_count_threshold, sentence_delimiter
    )
    analyze_translation(filtered_sentences)

    reduced_sentences = reduce_sentences(filtered_sentences, start_ratio, end_ratio)

    if shuffle:
        random.shuffle(reduced_sentences)

    print(f"Generated {len(reduced_sentences)} sentences")
    with open(translation_file_name, "w") as f:
        f.write("\n".join(reduced_sentences))
