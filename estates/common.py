import re
import traceback
import unicodedata

def parameterize(string_to_clean, sep = '-'):
    parameterized_string = unicodedata.normalize('NFKD', string_to_clean).encode('ASCII', 'ignore').decode()
    parameterized_string = re.sub("[^a-zA-Z0-9\-_]+", sep, parameterized_string)

    if sep is not None and sep is not '':
        parameterized_string = re.sub('/#{re_sep}{2,}', sep, parameterized_string)
        parameterized_string = re.sub('^#{re_sep}|#{re_sep}$', sep, parameterized_string, re.I)

    return parameterized_string.lower()


def deep_strip(in_str):
    if not in_str:
        return None
    return re.sub(r'\s', '', in_str)


def joinstrip(in_str_arr):
    return ''.join(map(lambda s: s.strip(), in_str_arr))


def strip_number(in_str):
    if not in_str:
        return None
    return re.sub(r'\d', '', in_str)


def strip(in_str):
    if not in_str:
        return None
    return in_str.strip()


def extract_number_str(in_str):
    if not in_str:
        return None
    return re.sub(r'[^\d]', '', in_str)


def extract_number(in_str):
    res = extract_number_str(in_str)
    return int(res) if res else None

def write_error():
    with open("errors.log", "a") as f:
        traceback.print_exc(file=f)

