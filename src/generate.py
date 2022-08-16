import json
import math
from typing import Any

from analyze import (
    check_sentence_counts,
    get_sentence_char_counts,
    get_sorted_char_count,
)


def load_template_file(file_path: str) -> list[dict[str, Any]]:
    with open(file_path, "r") as f:
        return json.loads(f.read())


def generate_sentences(
    templates_file_name: str,
    template_start: int,
    template_end: int,
    start_ratio: float,
    end_ratio: float,
) -> list[str]:
    templates = load_template_file(templates_file_name)[template_start:template_end]

    generated_sentences: list[str] = []
    for idx, template in enumerate(templates):
        # Initialize the template list to the initial sentence template
        unfinished_sentences: list[str] = [template["sentence"]]
        for idx, option_group in enumerate(template["options"]):
            unfinished_sentences_buffer: list[str] = []
            for option in option_group:
                for sentence in unfinished_sentences:
                    unfinished_sentences_buffer.append(
                        sentence.replace(f"|{idx}", option).capitalize()
                    )
            # Overide the previous unfinished sentences with the new unfinished sentences
            unfinished_sentences = unfinished_sentences_buffer
        generated_sentences += unfinished_sentences

    selected_sentences = []
    for idx, sentence in enumerate(generated_sentences):
        den = idx * (end_ratio - start_ratio) / len(generated_sentences) + start_ratio
        mod = idx % (1 / den)
        if math.floor(mod) == 0:
            selected_sentences.append(sentence)

    return selected_sentences


def filter_sentences(text: str, char_count_threshold: int, delimiter: str):
    sorted_char_counts = get_sorted_char_count(text)
    sentence_char_counts = get_sentence_char_counts(text, sorted_char_counts)
    sentence_list = [
        sentence + delimiter
        for sentence, char_counts in sentence_char_counts.items()
        if check_sentence_counts(char_counts, char_count_threshold)
    ]

    return sentence_list
