#!/bin/bash
set -e

##### NOTE
# This assumes that you have OpenFST and the Python bindings installed

DATA_DIR=en-de
SCRIPT_DIR=assignment/pbmt
OUT_DIR=output-intersection
TRAIN_DATA=en-de/train.en-de.low.filt
#TRAIN_DATA=en-de/valid.en-de.low
# mkdir -p $OUT_DIR
#NULL_ALIGNMENT=--null_alignment
NULL_ALIGNMENT=

# *** Train n-gram language model and create an FST
python $SCRIPT_DIR/train-ngram.py $TRAIN_DATA.en $OUT_DIR/ngram-fst.txt

# *** Implement 1: Train IBM Model 1 and find alignment
python ibmpseudo_ppt_example.py --train_source $TRAIN_DATA.de --train_target $TRAIN_DATA.en --align_output $OUT_DIR/alignment.txt $NULL_ALIGNMENT
echo "Finished implement 1.1"
python ibmpseudo_ppt_example.py --train_source $TRAIN_DATA.en --train_target $TRAIN_DATA.de --align_output $OUT_DIR/alignment-reverse.txt $NULL_ALIGNMENT
python combine_intersection.py $OUT_DIR/alignment.txt $OUT_DIR/alignment-reverse.txt $OUT_DIR/alignment-combine.txt
echo "1.2"

# *** Implement 2: Extract and score phrases
python phrase_extract.py --train_source $TRAIN_DATA.de --train_target $TRAIN_DATA.en --align_output $OUT_DIR/alignment-combine.txt --phrase_output $OUT_DIR/phrase.txt $NULL_ALIGNMENT
echo "Finished implement 2 "

# *** Implement 3: Create WFSTs for phrases
python create-phrase-fst.py $OUT_DIR/phrase.txt $OUT_DIR/phrase-fst.txt

echo "Finished implement 3 "

# *** Compile WFSTs into a single model
python $SCRIPT_DIR/symbols.py 2 < $OUT_DIR/phrase-fst.txt > $OUT_DIR/phrase-fst.isym
python $SCRIPT_DIR/symbols.py 2 < $OUT_DIR/ngram-fst.txt > $OUT_DIR/ngram-fst.isym
fstcompile --isymbols=$OUT_DIR/ngram-fst.isym --osymbols=$OUT_DIR/ngram-fst.isym $OUT_DIR/ngram-fst.txt | fstarcsort > $OUT_DIR/ngram-fst.fst
fstcompile --isymbols=$OUT_DIR/phrase-fst.isym --osymbols=$OUT_DIR/ngram-fst.isym $OUT_DIR/phrase-fst.txt | fstarcsort > $OUT_DIR/phrase-fst.fst

echo "Finished compiling WFST "

# *** Normally we could do this for efficiency purposes, but it takes a lot of memory, so we keep the FSTs separate
# fstcompose $OUT_DIR/phrase-fst.fst $OUT_DIR/ngram-fst.fst | fstarcsort > $OUT_DIR/tm-fst.fst

# *** Compose and find the best path for each WFST
for f in valid test blind; do
  echo "python $SCRIPT_DIR/decode.py $OUT_DIR/phrase-fst.fst $OUT_DIR/ngram-fst.fst $OUT_DIR/phrase-fst.isym $OUT_DIR/ngram-fst.isym < $DATA_DIR/$f.en-de.low.de > $OUT_DIR/$f.baseline.en"
  python $SCRIPT_DIR/decode.py $OUT_DIR/phrase-fst.fst $OUT_DIR/ngram-fst.fst $OUT_DIR/phrase-fst.isym $OUT_DIR/ngram-fst.isym < $DATA_DIR/$f.en-de.low.de > $OUT_DIR/$f.baseline.en
  if [[ -e $DATA_DIR/$f.en-de.low.en ]]; then
    perl $SCRIPT_DIR/multi-bleu.perl $DATA_DIR/$f.en-de.low.en < $OUT_DIR/$f.baseline.en
  fi
done
