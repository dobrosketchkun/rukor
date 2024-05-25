// ==UserScript==
// @name         RuKor
// @namespace    http://tampermonkey.net/
// @author       https://github.com/dobrosketchkun
// @version      1.1
// @description  RuKor is an art-project user script
// @match        http://*/*
// @match        https://*/*
// @grant        none
// @license      The Uncertain Commons License https://gist.github.com/dobrosketchkun/d0c6aba085fb4a910926616a8b83c4c5
// ==/UserScript==

(function() {
    'use strict';

    // Select algorithm version: 'v1' or 'v2'
    var algorithmVersion = 'v2';

    var transliteration_table = {
        'А': 'ㅏ', 'а': 'ㅏ',
        'Б': 'ㅂ', 'б': 'ㅂ',
        'В': '버', 'в': '버',
        'Г': 'ㄱ', 'г': 'ㄱ',
        'Д': 'ㄷ', 'д': 'ㄷ',
        'Е': 'ㅖ', 'е': 'ㅖ',
        'Ё': 'ㅛ', 'ё': 'ㅛ',
        'Ж': 'ㅈ', 'ж': 'ㅈ',
        'З': '서', 'з': '서',
        'И': 'ㅣ', 'и': 'ㅣ',
        'Й': 'ㅕ', 'й': 'ㅕ',
        'К': 'ㅋ', 'к': 'ㅋ',
        'Л': 'ㄹ', 'л': 'ㄹ',
        'М': 'ㅁ', 'м': 'ㅁ',
        'Н': 'ㄴ', 'н': 'ㄴ',
        'О': 'ㅗ', 'о': 'ㅗ',
        'П': 'ㅍ', 'п': 'ㅍ',
        'Р': '러', 'р': '러',
        'С': 'ㅅ', 'с': 'ㅅ',
        'Т': 'ㅌ', 'т': 'ㅌ',
        'У': 'ㅜ', 'у': 'ㅜ',
        'Ф': 'ㅃ', 'ф': 'ㅃ',
        'Х': 'ㅎ', 'х': 'ㅎ',
        'Ц': '터', 'ц': '터',
        'Ч': 'ㅊ', 'ч': 'ㅊ',
        'Ш': 'ㅆ', 'ш': 'ㅆ',
        'Щ': 'ㅉ', 'щ': 'ㅉ',
        'Ъ': 'ㅒ', 'ъ': 'ㅒ',
        'Ы': 'ㅡ', 'ы': 'ㅡ',
        'Ь': 'ㅔ', 'ь': 'ㅔ',
        'Э': 'ㅐ', 'э': 'ㅐ',
        'Ю': 'ㅠ', 'ю': 'ㅠ',
        'Я': 'ㅑ', 'я': 'ㅑ'
    };

    var CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    var JUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    var JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    function combineHangulCharsExtended(hangulString) {
        var result = "";
        var i = 0;
        while (i < hangulString.length) {
            var current = hangulString[i];
            var next = hangulString[i + 1] || "";
            var nextNext = hangulString[i + 2] || "";

            if (CHO.includes(current) && JUNG.includes(next)) {
                var choIdx = CHO.indexOf(current);
                var jungIdx = JUNG.indexOf(next);
                var jongIdx = JONG.indexOf(nextNext) > 0 ? JONG.indexOf(nextNext) : 0;
                var unicodeVal = 0xAC00 + (choIdx * 21 + jungIdx) * 28 + jongIdx;
                result += String.fromCharCode(unicodeVal);
                i += jongIdx > 0 ? 3 : 2;
            } else if (JUNG.includes(current)) {
                var choIdx = CHO.indexOf("ㅇ");
                var jungIdx = JUNG.indexOf(current);
                var unicodeVal = 0xAC00 + (choIdx * 21 + jungIdx) * 28;
                result += String.fromCharCode(unicodeVal);
                i++;
            } else {
                result += current;
                i++;
            }
        }
        return result;
    }

    function transliterate(text) {
        var transliterated = '';
        for (var i = 0; i < text.length; i++) {
            var char = text[i];
            transliterated += transliteration_table[char] || char;
        }
        return transliterated;
    }

    function isVowel(char) {
        return 'аеёиоуыэюяАЕЁИОУЫЭЮЯ'.includes(char);
    }

    function syllabify(word) {
        var vowelPositions = [];
        for (var i = 0; i < word.length; i++) {
            if (isVowel(word[i])) {
                vowelPositions.push(i);
            }
        }

        if (vowelPositions.length === 0) {
            return word;
        }

        var syllables = [];
        var start = 0;
        for (var i = 1; i < vowelPositions.length; i++) {
            var end = vowelPositions[i - 1] + 1;
            var nextVowel = vowelPositions[i];
            if (nextVowel - end > 1) {
                end = nextVowel - 1;
            }
            syllables.push(word.substring(start, end));
            start = end;
        }
        syllables.push(word.substring(start));
        return syllables.join('-');
    }

    function breakTextIntoSyllables(text) {
        var result = [];
        var buffer = '';
        var russianWordPattern = /[а-яА-ЯёЁ]+/;
        var i = 0;
        while (i < text.length) {
            var char = text[i];
            if (russianWordPattern.test(char)) {
                if (buffer) {
                    result.push(buffer);
                    buffer = '';
                }
                var russianWord = '';
                while (i < text.length && russianWordPattern.test(text[i])) {
                    russianWord += text[i];
                    i++;
                }
                var syllabifiedWord = syllabify(russianWord);
                result = result.concat(syllabifiedWord.split('-'));
            } else {
                buffer += char;
                i++;
            }
        }
        if (buffer) {
            result.push(buffer);
        }
        return result;
    }

    function alg_v1(input_text, transliteration_table) {
        var transliterated_text = transliterate(input_text, transliteration_table);
        var final_text = combineHangulCharsExtended(transliterated_text);
        return final_text;
    }

    function alg_v2(input_text, transliteration_table) {
        var syllabified_text = breakTextIntoSyllables(input_text);
        var final_text = '';
        for (var syl of syllabified_text) {
            var transliterated_text = transliterate(syl, transliteration_table);
            var syl_final_text = combineHangulCharsExtended(transliterated_text);
            final_text += syl_final_text;
        }
        return final_text;
    }

    function algorithm(input_text, transliteration_table, version) {
        if (version === 'v1') {
            return alg_v1(input_text, transliteration_table);
        } else if (version === 'v2') {
            return alg_v2(input_text, transliteration_table);
        } else {
            throw new Error("Sorry, you can use only 'v1' or 'v2' versions!");
        }
    }

    function replaceText() {
        var elements = document.querySelectorAll('*:not(script):not(style)');
        elements.forEach(function(element) {
            var node = element.firstChild;
            while (node) {
                if (node.nodeType === Node.TEXT_NODE) {
                    var transliterated = algorithm(node.nodeValue, transliteration_table, algorithmVersion);
                    node.nodeValue = transliterated;
                }
                node = node.nextSibling;
            }
        });
    }

    replaceText();
})();
