import sys
import argparse
import re

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

VOWELS = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
CONSONANTS = "бвгджзйклмнпрстфхцчшщБВГДЖЗЙКЛМНПРСТФХЦЧШЩ"


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



def is_vowel(char):
    return char in VOWELS

def syllabify(word):
    # Find all vowel positions
    vowel_positions = [i for i, char in enumerate(word) if is_vowel(char)]
    
    if not vowel_positions:
        return word  # No vowels, return the word as is
    
    syllables = []
    start = 0
    
    for i in range(1, len(vowel_positions)):
        end = vowel_positions[i-1] + 1
        next_vowel = vowel_positions[i]
        if next_vowel - end > 1:
            end = next_vowel - 1
        syllables.append(word[start:end])
        start = end
    
    # Append the last syllable
    syllables.append(word[start:])
    
    return '-'.join(syllables)

def break_text_into_syllables(text):
    result = []
    buffer = ""
    russian_word_pattern = re.compile(r'[а-яА-ЯёЁ]+')

    i = 0
    while i < len(text):
        char = text[i]
        if russian_word_pattern.match(char):
            if buffer:
                result.append(buffer)
                buffer = ""
            russian_word = ""
            while i < len(text) and russian_word_pattern.match(text[i]):
                russian_word += text[i]
                i += 1
            syllabified_word = syllabify(russian_word)
            result.extend(syllabified_word.split('-'))
        else:
            buffer += char
            i += 1

    if buffer:
        result.append(buffer)

    return result

def alg_v1(input_text, transliteration_table):
  transliterated_text = transliterate(input_text, transliteration_table)
  final_text = combine_hangul_chars_extended(transliterated_text)
  return final_text

def alg_v2(input_text, transliteration_table):
  syllabified_text = break_text_into_syllables(input_text)

  final_text = ''

  for syl in syllabified_text:
    transliterated_text = transliterate(syl, transliteration_table)
    syl_final_text = combine_hangul_chars_extended(transliterated_text)
    final_text += syl_final_text
  return final_text


def algorithm(input_text, transliteration_table, version):
  if version == 'v1':
    return alg_v1(input_text, transliteration_table)
  elif version == 'v2':
    return alg_v2(input_text, transliteration_table)
  else:
    raise Exception("Sorry, you can use only v1 or v2 versions!")

def main():
    parser = argparse.ArgumentParser(description='Transliterate text into Hangul syllable blocks.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Read text from a file.')
    group.add_argument('-t', '--text', help='Direct text input to transliterate.')
    parser.add_argument('-v', '--version', help='Version selection - v1, v2. The first version takes each letter in a sequence and combines them, the second version pre-divides words into syllables and only then gives them to the algorithm.', required=True)
    parser.add_argument('-o', '--output', help='The output file to save the result.', default=None)

    args = parser.parse_args()

    try:
        
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as file:
                input_text = file.read()
        elif args.text:
            input_text = args.text
        
        final_text = algorithm(input_text, transliteration_table, version = args.version)

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
