from zipfile import ZipFile
from bs4 import BeautifulSoup
import csv
import os


PROJ_DIR = os.path.abspath(os.getcwd())
EPUBS_DIR = os.path.join(PROJ_DIR, 'epubs')


def soup_list_from_epub(epub_fp, only_tags=''):
    '''Parses epub file and returns a list of soups from the contained
    html files within.'''
    soups = []
    with ZipFile(epub_fp, mode='r') as epub:
        html_list = sorted([item for item in epub.namelist() if 'html' in item])
        for html_file in html_list:
            with epub.open(html_file) as raw_html:
                soups.append(BeautifulSoup(raw_html, features="html.parser"))
    return soups


def soups_with_string(query_string, souplist, require_exact=False):
    '''Locates and returns any soups within a list of soups if given
    query_string is in the soup.'''
    soups_with_query = []

    lc_query_string = query_string.lower()
    print(f'query string: "{query_string}"')
    for soup in souplist:
        for paragraph in soup.strings:
            if lc_query_string in paragraph.lower():
                if require_exact:
                    if not next_char_is_alphanum(query_string, paragraph):
                        soups_with_query.append(soup)
                else:
                    soups_with_query.append(soup)
    return soups_with_query


def get_word_list(souplist, min_len):
    words = {}
    words['TOTAL'] = 0
    words['UNIQUE'] = 0

    for soup in souplist:
        for paragraph in soup.strings:
            paragraph = str(paragraph).replace('\n', '').split(' ')
            w_list = [sym_strip(word).lower() for word in paragraph]
            w_list = [word for word in w_list if len(word) >= min_len]
            for word in w_list:
                if word in words.keys():
                    words[word] += 1
                else:
                    words[word] = 1
                    words['UNIQUE'] += 1
                words['TOTAL'] += 1
    words = sorted(words.items(), key=lambda kv: kv[1], reverse=True)
    return words


def next_char_is_alphanum(substring, strng):
    next_char = strng.split(substring)
    if len(next_char) == 1:
        return False
    next_char = next_char[1][:1]
    if next_char.isalnum():
        return True


def sym_strip(string):
    '''Returns a given string with any non-alphanumeric characters removed.'''
    non_alnums = []
    for char in string:
        if char not in non_alnums and not char.isalnum():
            non_alnums.append(char)
    while non_alnums:
        string = string.replace(non_alnums.pop(), '')
    return string


if __name__ == '__main__':
    in_files = [file for file in os.listdir(EPUBS_DIR) if file[-5:] == '.epub']
    for file in in_files:
        souplist = soup_list_from_epub(os.path.join(EPUBS_DIR, file))
        words_csv = 'words_from_' + file[:-5] + '.csv'
        with open(words_csv, 'w') as writefile:
            writer = csv.writer(writefile)
            for pair in get_word_list(souplist, 2):
                writer.writerow([pair[0], pair[1]])
