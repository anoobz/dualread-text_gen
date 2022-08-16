import json, random, re
import math
from dotenv import load_dotenv
from typing import Any

from mongodb import MongoDatabase
from translate_client import TranslateClient

load_dotenv()


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


def count_word(word: str, text: str) -> int:
    regex = re.compile(r"\b%s\b" % word)
    return len(re.findall(regex, text))


def load_words(word_type: str, limit: int) -> dict[str, list[str]]:
    with open(f"list_{limit}/{word_type}.json", "r") as f:
        return json.loads(f.read())


def get_word_counts(
    text: str, word_types: list[str], limit: int
) -> dict[str, dict[str, int]]:
    word_counts = {}
    for word_type in word_types:
        word_counts[word_type] = {}
        for word, variations in load_words(word_type, limit).items():
            count = 0
            for variation in variations:
                count += count_word(variation, text)

            word_counts[word_type][word] = count

    return word_counts


def get_sorted_char_count(text: str) -> dict[str, int]:
    char_counts = {}
    text_characters = re.sub(r"\W+", "", text, flags=re.UNICODE)
    for char in text_characters:
        char_counts[char] = char_counts.get(char, 0) + 1

    sorted_char_counts = dict(
        sorted(char_counts.items(), key=lambda count: count[1], reverse=True)
    )

    return sorted_char_counts


def analyze_generation(text: str):
    word_set = set([word.lower() for word in re.split(r"\W+", text)])
    word_counts = get_word_counts(text, ["verbs", "nouns", "adjectives"], limit=5)
    print(f"Unique word count: {len(word_set)}")
    print(word_set)
    print(word_counts)


def get_sentence_char_counts(
    text: str, total_char_count: dict[str, int]
) -> dict[str, dict[str, int]]:
    sentence_char_counts = {}
    trimed_text = re.sub(r"[^\w\n]", "", text, flags=re.UNICODE)
    sentence_list = re.split(r"\n", trimed_text, flags=re.UNICODE)
    for sentence in sentence_list:
        temp_char_counts = {}
        for char in sentence:
            temp_char_counts[char] = total_char_count.get(char, 0)

        sentence_char_counts[sentence] = dict(
            sorted(temp_char_counts.items(), key=lambda count: count[1], reverse=True)
        )

    return sentence_char_counts


def check_sentence_counts(
    char_counts: dict[str, int], char_count_threshold: int
) -> bool:
    for count in char_counts.values():
        if count <= char_count_threshold:
            return False
    return True


def filter_sentences(text: str, char_count_threshold: int, delimiter: str):
    sorted_char_counts = get_sorted_char_count(text)
    sentence_char_counts = get_sentence_char_counts(text, sorted_char_counts)
    sentence_list = [
        sentence + delimiter
        for sentence, char_counts in sentence_char_counts.items()
        if check_sentence_counts(char_counts, char_count_threshold)
    ]

    return sentence_list


def analyze_translation(text: str):
    sorted_char_counts = get_sorted_char_count(text)
    print(f"Char count: {len(sorted_char_counts)}")
    print(sorted_char_counts)


if __name__ == "__main__":
    mongo_client = MongoDatabase()
    translate_client = TranslateClient()
    source_language = "en"
    target_language = "zh-CN"
    template_start = 0
    template_end = template_start + 10
    start_ratio = 0.1
    end_ratio = 1
    templates_file_name = "templates.json"
    generation_file_name = "generated_sentences.txt"
    translation_file_name = "filtered_translated_sentences.txt"
    char_count_threshold = 0
    sentence_delimiter = "。"
    shuffle = True

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
