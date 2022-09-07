import json, re
from words.hsk1_words import vocab

output_folder = "analyze"


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
    word_count = {}
    for word in re.split(r"\W+", text):
        word = word.lower()
        word_count[word] = word_count.get(word, 0) + 1

    word_count = dict(
        sorted(word_count.items(), key=lambda count: count[1], reverse=True)
    )
    print(f"Unique word count: {len(word_count)}")

    with open(f"{output_folder}/unique_word_counts.json", "w") as f:
        f.write(json.dumps(word_count))

    with open(f"{output_folder}/vocab_counts.json", "w") as f:
        f.write(json.dumps(get_vocab_word_counts(word_count)))


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
        if count < char_count_threshold:
            return False
    return True


def analyze_translation(translated_sentences: list[str]):
    sorted_char_counts = get_sorted_char_count("".join(translated_sentences))
    print(f"Char count: {len(sorted_char_counts)}")

    with open(f"{output_folder}/char_counts.json", "w") as f:
        f.write(json.dumps(sorted_char_counts, ensure_ascii=False))


def get_vocab_word_counts(unique_counts: dict[str, int]):
    vocab_word_counts = {}
    for word_type, words in vocab.items():
        vocab_word_counts[word_type] = {}
        for word, options in words.items():
            for option in options:
                vocab_word_counts[word_type][word] = vocab_word_counts[word_type].get(
                    word, 0
                ) + unique_counts.get(option, 0)
    return vocab_word_counts


if __name__ == "__main__":
    text = "I am a cat. I am a dog."
    word_count = {}
    for word in re.split(r"\W+", text):
        word = word.lower()
        word_count[word] = word_count.get(word, 0) + 1

    word_count = dict(
        sorted(word_count.items(), key=lambda count: count[1], reverse=True)
    )
    counts = get_vocab_word_counts(word_count)
    print(counts)
