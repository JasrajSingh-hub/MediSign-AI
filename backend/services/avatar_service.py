import string


def parse_avatar_text(raw_text: str) -> dict:
    clean_text = raw_text.lower().translate(str.maketrans("", "", string.punctuation))
    words = clean_text.split()
    final_token_sequence = []

    for word in words:
        for letter in word:
            if letter.isalpha():
                final_token_sequence.append(letter.upper())
        final_token_sequence.append("SPACE")

    if final_token_sequence and final_token_sequence[-1] == "SPACE":
        final_token_sequence.pop()

    return {
        "status": "success",
        "original_text": raw_text,
        "tokens": final_token_sequence,
    }
