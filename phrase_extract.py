# -*- encoding: utf-8 -*-

import argparse
from itertools import chain

import numpy as np
from collections import defaultdict, Counter

'''
Determine whether set of values is quasi-consecutive
  Examples:
    {1, 2, 3, 4, 5, 6} => True
    {4, 2, 3} => True (equivalent to {2, 3, 4})
    {3} => True
    {1, 2, 4} => True if word at position 3 is not aligned to anything, False otherwise
'''

allow_null_alignment = True

if allow_null_alignment:
    from ibmpseudo_ppt_example import read_bitext_file
else:
    from ibmpseudo_ppt_example_original_direction import read_bitext_file


def quasi_consec(tp, A):
    minTP = min(tp)
    maxTP = max(tp)
    flag = True
    for j in range(minTP, maxTP):
        if not j in tp:
            if allow_null_alignment and not (j in A[0].keys()):
                flag = False
    return flag


'''
Given an alignment, extract phrases consistent with the alignment
  Input:
    -e_aligned_words: mapping between E-side words (positions) and aligned F-side words (positions)
    -f_aligned_words: mapping between F-side words (positions) and aligned E-side words (positions)
    -e: E sentence
    -f: F sentence
  Return list of extracted phrases
'''


# def phrase_extract(self, e_aligned_words, f_aligned_words, e, f):
def phrase_extract(A, e, f, max_n):
    extracted_phrases = []
    # Loop over all substrings in the E
    if allow_null_alignment:
        start = 1
    else:
        start = 0
    for i1 in range(start, len(e)):
        for i2 in range(i1, i1 + max_n):
            # Get all positions in F that correspond to the substring from i1 to i2 in E (inclusive)
            tp = [list(A[i].keys()) for i in range(i1, i2 + 1)]
            tp = list(chain.from_iterable(tp))
            if len(tp) != 0 and quasi_consec(tp, A):
                j1 = min(tp)
                j2 = max(tp)  # max TP
                # Get all positions in E that correspond to the substring from j1 to j2 in F (inclusive)
                sp = [i for i in A.keys() for j in A[i].keys() if j1 <= j and j <= j2]
                if len(sp) != 0 and min(sp) >= i1 and max(
                        sp) <= i2:  # Check that all elements in sp fall between i1 and i2 (inclusive)
                    e_phrase = " ".join(e[i1:i2 + 1])
                    f_phrase = " ".join(f[j1:j2 + 1])
                    if (i2+1-i1)<=max_n and (j2+1-j1)<=max_n:
                        extracted_phrases.append((e_phrase, f_phrase))
                    # Extend source phrase by adding unaligned words
                    j1 -= 1
                    while j1 >= 0 and allow_null_alignment and j1 in A[0].keys():  # Check that j1 is unaligned
                        j_prime = j2 + 1
                        while j_prime < len(f) and allow_null_alignment and j_prime in A[
                            0].keys():  # Check that j2 is unaligned
                            f_phrase = " ".join(f[j1:j_prime + 1])
                            if (i2+1-i1)<=max_n and (j_prime+1-j1)<=max_n:
                                extracted_phrases += [(e_phrase, f_phrase)]
                            j_prime += 1
                        j1 -= 1

    return extracted_phrases


def align(bitext, align_output, phrase_output, max_n):
    extracted_phrases_aross_corpus = []
    align_output_lines = open(align_output, "r").readlines()
    for idx, (e, f) in enumerate(bitext):
        if True:
            if idx % (len(bitext) / 10) == 0:
                print idx
            pairs = align_output_lines[idx].strip().split()
            A = defaultdict(lambda: defaultdict(lambda: 0))

            for pair in pairs:
                A[int(pair.split('-')[0])][int(pair.split('-')[1])] = 1
            extracted_phrases_aross_corpus += phrase_extract(A, e, f, max_n)

    f_write = open(phrase_output, "w")
    print extracted_phrases_aross_corpus[:5]
    counter = Counter(extracted_phrases_aross_corpus)
    for (e_phrase, f_phrase) in counter.keys():
        f_write.write(f_phrase + "\t" + e_phrase + "\t" + str(np.log(counter[(e_phrase, f_phrase)])) + "\n")
    return extracted_phrases_aross_corpus


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--train_source', type=str, default="./en-de/valid.en-de.low.de")
    parser.add_argument('--train_target', type=str, default="./en-de/valid.en-de.low.en")
    if allow_null_alignment:
        parser.add_argument('--align_output', type=str, default="./output/alignment.txt")
    else:
        parser.add_argument('--align_output', type=str, default="./output-valid/alignment.txt")

    parser.add_argument('--phrase_output', type=str, default="./output/phrase.txt")
    parser.add_argument('--max_n', type=int, default=3)

    args = parser.parse_args()

    bitext = read_bitext_file(args.train_target,
                              args.train_source)

    align(bitext, args.align_output, args.phrase_output, args.max_n)
