import unicodedata


inverse_mapping_table = {
    # 0110
    u"Đ": [
        u"Ð",  # 00D0
        u"Ɖ",  # 0189
        u"ᴆ",  # 1D06
    ]
}

mapping_table = {}
for key, characters in inverse_mapping_table.items():
    for character in characters:
        mapping_table[character] = key


def map_character_to_tcvn(c):
    if c in mapping_table:
        return mapping_table[c]
    else:
        return c


def map_text_to_tcvn(text):
    """
    @param unicode text: converted to normalize nfc form
    """
    return [map_character_to_tcvn(c) for c in text]


def vietnamese_normalize(text):
    """
    @param text: unicode
    """
    text = unicodedata.normalize("NFC", text)
    text = map_text_to_tcvn(text)
    return "".join(text)


if __name__ == '__main__':
    s = 'Giỏi'
    s1 = b'Gio\xcc\x89i'.decode()
    s2 = b'Gi\xe1\xbb\x8fi'.decode()
    s1 = vietnamese_normalize(s1)
    s2 = vietnamese_normalize(s2)

    print(s.encode() == s2.encode())
