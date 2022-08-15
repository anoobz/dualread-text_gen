import json, random, re
from dotenv import load_dotenv
from typing import Any, Optional

from models.translation import Translation
from mongodb import MongoDatabase
from translate_client import TranslateClient

load_dotenv()


def load_template_file(file_path: str) -> list[dict[str, Any]]:
    with open(file_path, "r") as f:
        return json.loads(f.read())


def save_sentences_to_file(text: str):
    with open("generated_sentences.txt", "w") as f:
        f.write(text)


def generate_sentences(templates: list[dict[str, Any]]) -> list[str]:
    generated_sentences: list[str] = []
    for template in templates:
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
    return generated_sentences


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


def generate_shuffled_sentence_list(limit: Optional[int] = None) -> list[str]:
    templates = load_template_file("template_limited_words.json")

    if limit:
        templates = templates[:limit]

    generated_sentences = generate_sentences(templates)
    random.shuffle(generated_sentences)

    return generated_sentences


def generate(limit: Optional[int] = None):
    generated_sentences = generate_shuffled_sentence_list(limit)
    print(f"generated {len(generated_sentences)} sentences")
    generated_text = "\n".join(generated_sentences)
    save_sentences_to_file(generated_text)


def get_sorted_char_count(text: str) -> dict[str, int]:
    char_counts = {}
    text_characters = re.sub(r"[\W\d_]+", "", text, flags=re.UNICODE)
    for char in text_characters:
        char_counts[char] = char_counts.get(char, 0) + 1

    sorted_char_counts = dict(
        sorted(char_counts.items(), key=lambda count: count[1], reverse=True)
    )

    return sorted_char_counts


def analyze_generation(file_name: str):
    with open(file_name, "r") as f:
        text = f.read()

    word_set = set([word.lower() for word in re.split(r"[\W\d_]+", text)])
    word_counts = get_word_counts(text, ["verbs", "nouns", "adjectives"], limit=5)
    print(f"Unique word count: {len(word_set)}")
    print(word_set)
    print(word_counts)


def get_sentence_char_counts(
    text: str, total_char_count: dict[str, int]
) -> dict[str, dict[str, int]]:
    sentence_char_counts = {}
    trimed_text = re.sub(r"[^\w \n]", "", text, flags=re.UNICODE)
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


def filter_sentences(file_name: str, char_count_threshold: int):
    with open(file_name, "r") as f:
        text = f.read()

    sorted_char_counts = get_sorted_char_count(text)
    sentence_char_counts = get_sentence_char_counts(text, sorted_char_counts)
    sentence_list = [
        sentence
        for sentence, char_counts in sentence_char_counts.items()
        if check_sentence_counts(char_counts, char_count_threshold)
    ]

    with open("filtered_translated_sentences.txt", "w") as f:
        f.write("。\n".join(sentence_list))


def analyze_translation(file_name: str):
    with open(file_name, "r") as f:
        text = f.read()

    sorted_char_counts = get_sorted_char_count(text)
    print(f"Char count: {len(sorted_char_counts)}")
    print(sorted_char_counts)

    sentence_char_counts = get_sentence_char_counts(text, sorted_char_counts)

    with open("translation_counts.json", "w") as f:
        f.write(json.dumps(sentence_char_counts, ensure_ascii=False))


if __name__ == "__main__":
    translate_client = TranslateClient()
    print(translate_client.translate("I am a cat", "en", "fr"))
