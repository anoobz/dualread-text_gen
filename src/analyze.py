import json, re


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
        if count < char_count_threshold:
            return False
    return True


def analyze_translation(text: str):
    sorted_char_counts = get_sorted_char_count(text)
    print(f"Char count: {len(sorted_char_counts)}")
    print(sorted_char_counts)
