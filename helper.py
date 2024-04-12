def chunks_split(ll, n):
    for i in range(0, len(ll), n):
        yield ll[i:i + n]


def text_chunks(text, n):
    lines = text.split('\n')
    lines_per_chunk = n
    return chunks_split(lines, lines_per_chunk)


# In input sentence (old), replace recognised NE with tagged NE (new):
# start, end are indexes of NE
def replace_string(old, new, start, end):
    first = old[:start]
    last = old[end:]
    return first + new + last

def translit(x):
    mapping = {
    'Љ': 'Lj',
    'Њ': 'Nj',
    'Џ': 'Dž',
    'А': 'A',
    'Б': 'B',
    'В': 'V',
    'Г': 'G',
    'Д': 'D',
    'Ђ': 'Đ',
    'Е': 'E',
    'Ж': 'Ž',
    'З': 'Z',
    'И': 'I',
    'Ј': 'J',
    'К': 'K',
    'Л': 'L',
    'М': 'M',
    'Н': 'N',
    'О': 'O',
    'П': 'P',
    'Р': 'R',
    'С': 'S',
    'Т': 'T',
    'Ћ': 'Ć',
    'У': 'U',
    'Ф': 'F',
    'Х': 'H',
    'Ц': 'C',
    'Ч': 'Č',
    'Ш': 'Š',
    'љ': 'lj',
    'њ': 'nj',
    'џ': 'dž',
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'ђ': 'đ',
    'е': 'e',
    'ж': 'ž',
    'з': 'z',
    'и': 'i',
    'ј': 'j',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'ћ': 'ć',
    'у': 'u',
    'ф': 'f',
    'х': 'h',
    'ц': 'c',
    'ч': 'č',
    'ш': 'š'
    }
    for key in mapping.keys():
        x = (x.replace(key, mapping[key]))
    return x