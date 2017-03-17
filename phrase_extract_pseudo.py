# -*- encoding: utf-8 -*-
'''
Determine whether set of values is quasi-consecutive
  Examples:
    {1, 2, 3, 4, 5, 6} => True
    {4, 2, 3} => True (equivalent to {2, 3, 4})
    {3} => True
    {1, 2, 4} => True if word at position 3 is not aligned to anything, False otherwise
'''
def quasi_consec(tp, aligned_words):
  TODO

'''
Given an alignment, extract phrases consistent with the alignment
  Input:
    -e_aligned_words: mapping between E-side words (positions) and aligned F-side words (positions)
    -f_aligned_words: mapping between F-side words (positions) and aligned E-side words (positions)
    -e: E sentence
    -f: F sentence
  Return list of extracted phrases
'''
def phrase_extract(self, e_aligned_words, f_aligned_words, e, f):
  extracted_phrases = []
  # Loop over all substrings in the E
  for i1 in range(len(e)):
    for i2 in range(i1, len(e)):
      # Get all positions in F that correspond to the substring from i1 to i2 in E (inclusive)
      tp = TODO 
      if len(tp) != 0 and quasi_consec(tp, f_aligned_words):
        j1 = TODO # min TP
        j2 = TODO # max TP
        # Get all positions in E that correspond to the substring from j1 to j2 in F (inclusive)
        sp = TODO
        if len(sp) != 0 and TODO: # Check that all elements in sp fall between i1 and i2 (inclusive)
          e_phrase = e[i1:i2+1]
          f_phrase = f[j1:j2+1]
          extracted_phrases.append((e_phrase, f_phrase))
          # Extend source phrase by adding unaligned words
          while j1 >= 0 and TODO: # Check that j1 is unaligned
            j_prime = j2
            while j_prime < len(f) and TODO: # Check that j2 is unaligned
              f_phrase = f[j1:j_prime+1]
              extracted_phrases.append((e_phrase, f_phrase))
              j_prime += 1
            j1 -= 1

  return extracted_phrases
