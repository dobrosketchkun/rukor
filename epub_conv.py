import os
import re
import zipfile
import argparse
from bs4 import BeautifulSoup
from lxml import etree
import warnings

# Transliteration table
transliteration_table = {
    'А': 'ㅏ', 'а': 'ㅏ', 'Б': 'ㅂ', 'б': 'ㅂ', 'В': '버', 'в': '버', 'Г': 'ㄱ', 'г': 'ㄱ',
    'Д': 'ㄷ', 'д': 'ㄷ', 'Е': 'ㅖ', 'е': 'ㅖ', 'Ё': 'ㅛ', 'ё': 'ㅛ', 'Ж': 'ㅈ', 'ж': 'ㅈ',
    'З': '서', 'з': '서', 'И': 'ㅣ', 'и': 'ㅣ', 'Й': 'ㅕ', 'й': 'ㅕ', 'К': 'ㅋ', 'к': 'ㅋ',
    'Л': 'ㄹ', 'л': 'ㄹ', 'М': 'ㅁ', 'м': 'ㅁ', 'Н': 'ㄴ', 'н': 'ㄴ', 'О': 'ㅗ', 'о': 'ㅗ',
    'П': 'ㅍ', 'п': 'ㅍ', 'Р': '러', 'р': '러', 'С': 'ㅅ', 'с': 'ㅅ', 'Т': 'ㅌ', 'т': 'ㅌ',
    'У': 'ㅜ', 'у': 'ㅜ', 'Ф': 'ㅃ', 'ф': 'ㅃ', 'Х': 'ㅎ', 'х': 'ㅎ', 'Ц': '터', 'ц': '터',
    'Ч': 'ㅊ', 'ч': 'ㅊ', 'Ш': 'ㅆ', 'ш': 'ㅆ', 'Щ': 'ㅉ', 'щ': 'ㅉ', 'Ъ': 'ㅒ', 'ъ': 'ㅒ',
    'Ы': 'ㅡ', 'ы': 'ㅡ', 'Ь': 'ㅔ', 'ь': 'ㅔ', 'Э': 'ㅐ', 'э': 'ㅐ', 'Ю': 'ㅠ', 'ю': 'ㅠ',
    'Я': 'ㅑ', 'я': 'ㅑ'
}

CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
JUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

def combine_hangul_chars_extended(hangul_string):
    result = ""
    i = 0
    while i < len(hangul_string):
        current = hangul_string[i]
        next_char = hangul_string[i + 1] if i + 1 < len(hangul_string) else ""
        next_next = hangul_string[i + 2] if i + 2 < len(hangul_string) else ""

        if current in CHO and next_char in JUNG:
            cho_idx = CHO.index(current)
            jung_idx = JUNG.index(next_char)
            jong_idx = JONG.index(next_next) if next_next in JONG else 0
            unicode_val = 0xAC00 + (cho_idx * 21 + jung_idx) * 28 + jong_idx
            result += chr(unicode_val)
            i += 3 if jong_idx > 0 else 2
        elif current in JUNG:
            cho_idx = CHO.index("ㅇ")
            jung_idx = JUNG.index(current)
            unicode_val = 0xAC00 + (cho_idx * 21 + jung_idx) * 28
            result += chr(unicode_val)
            i += 1
        else:
            result += current
            i += 1
    return result

def transliterate(text):
    return ''.join(transliteration_table.get(char, char) for char in text)

def is_vowel(char):
    return char in 'аеёиоуыэюяАЕЁИОУЫЭЮЯ'

def syllabify(word):
    vowel_positions = [i for i, char in enumerate(word) if is_vowel(char)]
    
    if not vowel_positions:
        return word

    syllables = []
    start = 0
    for i in range(1, len(vowel_positions)):
        end = vowel_positions[i - 1] + 1
        next_vowel = vowel_positions[i]
        if next_vowel - end > 1:
            end = next_vowel - 1
        syllables.append(word[start:end])
        start = end
    syllables.append(word[start:])
    return '-'.join(syllables)

def break_text_into_syllables(text):
    result = []
    buffer = ''
    russian_word_pattern = re.compile(r'[а-яА-ЯёЁ]+')
    i = 0
    while i < len(text):
        if russian_word_pattern.match(text[i]):
            if buffer:
                result.append(buffer)
                buffer = ''
            russian_word = ''
            while i < len(text) and russian_word_pattern.match(text[i]):
                russian_word += text[i]
                i += 1
            syllabified_word = syllabify(russian_word)
            result.extend(syllabified_word.split('-'))
        else:
            buffer += text[i]
            i += 1
    if buffer:
        result.append(buffer)
    return result

def transliterate_hangul(input_text):
    syllabified_text = break_text_into_syllables(input_text)
    final_text = ''
    for syl in syllabified_text:
        transliterated_text = transliterate(syl)
        syl_final_text = combine_hangul_chars_extended(transliterated_text)
        final_text += syl_final_text
    return final_text

def process_epub(input_path, output_path):
    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        with zipfile.ZipFile(output_path, 'w') as zip_out:
            for file_info in zip_ref.infolist():
                with zip_ref.open(file_info) as file:
                    content = file.read()
                    
                    if file_info.filename.endswith(('.html', '.xhtml', '.htm', '.xml')):
                        # Process HTML/XML files
                        soup = BeautifulSoup(content, 'lxml-xml')
                        for text_node in soup.find_all(text=True):
                            if text_node.parent.name not in ['script', 'style']:
                                new_text = transliterate_hangul(text_node.string)
                                text_node.replace_with(new_text)
                        content = str(soup).encode('utf-8')
                    elif file_info.filename.endswith('.opf'):
                        # Process OPF files
                        tree = etree.fromstring(content)
                        for elem in tree.iter():
                            if elem.text:
                                elem.text = transliterate_hangul(elem.text)
                            if elem.tail:
                                elem.tail = transliterate_hangul(elem.tail)
                        content = etree.tostring(tree, encoding='utf-8', xml_declaration=True)
                    
                    zip_out.writestr(file_info, content)

def main():
    parser = argparse.ArgumentParser(description='Transliterate Russian text in EPUB files to Hangul. // Транслитерирует русский текст внутри epub формата в Хангыль')
    parser.add_argument('input', help='Input EPUB file path // Путь до epub файла')
    parser.add_argument('output', help='Output EPUB file path // Путь до места сохранения результата')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist. // ОШИБКА: Epub файл '{args.input}' не существует")
        return

    if os.path.exists(args.output):
        print(f"Warning: Output file '{args.output}' already exists. It will be overwritten. // ВНИМАНИЕ: Файл '{args.output}' уже существует и будет перезаписан.")

    try:
        process_epub(args.input, args.output)
        print(f"Transliteration complete. Output saved to '{args.output}' // Результат сохранён в '{args.output}'")
    except Exception as e:
        print(f"Error occurred during processing: {str(e)} // Произошла следующая ошибка: {str(e)}")

if __name__ == "__main__":
    main()
