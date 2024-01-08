import sys
import argparse

# Define the transliteration table
transliteration_table = {
    "А": "ㅏ", "а": "ㅏ",
    "Б": "ㅂ", "б": "ㅂ",
    "В": "버", "в": "버",
    "Г": "ㄱ", "г": "ㄱ",
    "Д": "ㄷ", "д": "ㄷ",
    "Е": "ㅖ", "е": "ㅖ",
    "Ё": "ㅛ", "ё": "ㅛ",
    "Ж": "ㅈ", "ж": "ㅈ",
    "З": "서", "з": "서",
    "И": "ㅣ", "и": "ㅣ",
    "Й": "ㅕ", "й": "ㅕ",
    "К": "ㅋ", "к": "ㅋ",
    "Л": "ㄹ", "л": "ㄹ",
    "М": "ㅁ", "м": "ㅁ",
    "Н": "ㄴ", "н": "ㄴ",
    "О": "ㅗ", "о": "ㅗ",
    "П": "ㅍ", "п": "ㅍ",
    "Р": "러", "р": "러",
    "С": "ㅅ", "с": "ㅅ",
    "Т": "ㅌ", "т": "ㅌ",
    "У": "ㅜ", "у": "ㅜ",
    "Ф": "ㅃ", "ф": "ㅃ",
    "Х": "ㅎ", "х": "ㅎ",
    "Ц": "터", "ц": "터",
    "Ч": "ㅊ", "ч": "ㅊ",
    "Ш": "ㅆ", "ш": "ㅆ",
    "Щ": "ㅉ", "щ": "ㅉ",
    "Ъ": "ㅒ", "ъ": "ㅒ",
    "Ы": "ㅡ", "ы": "ㅡ",
    "Ь": "ㅔ", "ь": "ㅔ",
    "Э": "ㅐ", "э": "ㅐ",
    "Ю": "ㅠ", "ю": "ㅠ",
    "Я": "ㅑ", "я": "ㅑ"
}

def transliterate(text, table):
    transliterated = ""
    for char in text:
        transliterated += table.get(char, char)  # Default to the original char if not in table
    return transliterated

def combine_hangul_chars_extended(hangul_string):
    CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    JUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
    JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

    result = ""
    i = 0
    while i < len(hangul_string):
        if hangul_string[i] in CHO and i + 1 < len(hangul_string) and hangul_string[i + 1] in JUNG:
            cho_idx = CHO.index(hangul_string[i])
            jung_idx = JUNG.index(hangul_string[i + 1])
            jong_idx = 0
            if i + 2 < len(hangul_string) and hangul_string[i + 2] in JONG:
                jong_idx = JONG.index(hangul_string[i + 2])
                i += 3
            else:
                i += 2
            unicode_val = 0xAC00 + (cho_idx * 21 + jung_idx) * 28 + jong_idx
            result += chr(unicode_val)
        elif hangul_string[i] in JUNG:
            cho_idx = CHO.index("ㅇ")  # Default to 'ㅇ' for lonely vowels
            jung_idx = JUNG.index(hangul_string[i])
            unicode_val = 0xAC00 + (cho_idx * 21 + jung_idx) * 28
            result += chr(unicode_val)
            i += 1
        else:
            result += hangul_string[i]
            i += 1
    return result

def main():
    parser = argparse.ArgumentParser(description='Transliterate text into Hangul syllable blocks.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Read text from a file.')
    group.add_argument('-t', '--text', help='Direct text input to transliterate.')
    parser.add_argument('-o', '--output', help='The output file to save the result.', default=None)

    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as file:
                input_text = file.read()
        elif args.text:
            input_text = args.text

        transliterated_text = transliterate(input_text, transliteration_table)
        final_text = combine_hangul_chars_extended(transliterated_text)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as outfile:
                outfile.write(final_text)
                print(f"Output saved to {args.output}")
        else:
            print(final_text)
    except FileNotFoundError:
        print(f"File not found: {args.file}")
        sys.exit(1)

if __name__ == '__main__':
    main()
