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

