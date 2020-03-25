from nltk.tokenize import sent_tokenize
import sys


def lines(a, b):
    """Return lines in both a and b"""

    # split file1 into lines
    file1_lines = a.split('\n')

    # split file2 into lines
    file2_lines = b.split('\n')

    # create empty list to store matches
    matches = []

    # add matching lines to matches, avoiding duplicates
    [matches.append(line) for line in file1_lines if line in file2_lines and line not in matches]

    return matches


def sentences(a, b):
    """Return sentences in both a and b"""

    # split file1 into sentences
    file1_tokens = sent_tokenize(a, language='english')

    # split file2 into sentences
    file2_tokens = sent_tokenize(b, language='english')

    # create empty list to store matches
    matches = []

    # add matching sentences to matches, avoiding duplicates
    [matches.append(token) for token in file1_tokens if token in file2_tokens and token not in matches]

    return matches


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    # split file1 into substrings of length n
    a = a.split('\n')
    a = ''.join(a)
    file1_substrings = [a[i:i+n] for i in range(0, len(a) - n + 1)]

    # split file2 into substrings of length n
    b = b.split('\n')
    b = ''.join(b)
    file2_substrings = [b[i:i+n] for i in range(0, len(a) - n + 1)]

    # create empty list to store matches
    matches = []

    # add matching substrings to matches, avoiding duplicates
    [matches.append(substring) for substring in file1_substrings if substring in file2_substrings and substring not in matches]

    return matches
