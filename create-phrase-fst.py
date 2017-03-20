from __future__ import print_function
import sys
import math
from collections import defaultdict

import os

print(os.path)

ctxts1 = 0.0  # total word count
ctxts2 = defaultdict(lambda: 0.0)  # bigram denominator count
count1 = defaultdict(lambda: 0.0)  # unigram count
count2 = defaultdict(lambda: 0.0)  # bigram count
stateid = defaultdict(lambda: len(stateid))

outfile = open(sys.argv[2], "w")

with open(sys.argv[1], "r") as infile:
    for line in infile:

        src = line.strip().split("\t")[0]
        tgt = line.strip().split("\t")[1]
        logProb = line.strip().split("\t")[2]

        vals = line.strip().split("\t") + ["</s>"]
        ctxt = "<s>"

        for idx, val in enumerate(src.split() + tgt.split()):
            text = src.split() + tgt.split()
            if idx > 0:
                prev_state = ctxt + " ".join(text[:idx])
            else:
                prev_state = ctxt

            next_state = ctxt + " ".join(text[:(idx + 1)])
            if idx <= len(src.split()):
                prev_label = False
            else:
                prev_label = True
            if idx <= (len(src.split()) - 1):
                next_label = False
            else:
                next_label = True

            if prev_label:
                cut_position=len(src.split())
            else:
                cut_position = 0
            prev_state=(prev_state,prev_label,cut_position)

            if next_label:
                cut_position=len(src.split())
            else:
                cut_position = 0
            next_state=(next_state,next_label,cut_position)

            # if idx > 0 and idx < len(src.split()):
            #     prev_state = ctxt + " ".join(text[:idx])
            # elif idx > 0 and idx == len(src.split()):
            #     prev_state = ctxt + src + " | "
            # elif idx > 0 and idx > len(src.split()):
            #     prev_state = ctxt + src + " | " + " ".join(text[len(src.split()):idx])
            # else:
            #     prev_state = ctxt
            #
            # if idx < len(src.split()) - 1:
            #     next_state = ctxt + " ".join(text[:(idx + 1)])
            # elif idx == (len(src.split()) - 1):
            #     next_state = ctxt + src + " | "
            # else:
            #     next_state = ctxt + src + " | " + " ".join(text[len(src.split()):(idx + 1)])



            if not prev_state in stateid or not next_state in stateid:
                if idx < len(src.split()):
                    print("%d %d %s <eps>" % (stateid[prev_state], stateid[next_state], val), file=outfile)
                else:
                    print("%d %d <eps> %s" % (stateid[prev_state], stateid[next_state], val), file=outfile)
            last_stateid = stateid[next_state]
            if not prev_state in stateid or not next_state in stateid:
                if idx < len(src.split()):
                    print("%d %d %s <eps>" % (stateid[prev_state], stateid[next_state], val), file=outfile)
                else:
                    print("%d %d <eps> %s" % (stateid[prev_state], stateid[next_state], val), file=outfile)
            last_stateid = stateid[next_state]

            # if "also" in line and "," in line and "so" in line and len(text)<=4:
            #     print(text, prev_state, stateid[prev_state],next_state,stateid[next_state]," ".join(text[len(src.split()):(idx + 1)]))

        print("%d 0 <eps> <eps> %s" % (last_stateid, logProb), file=outfile)

    print("0 0 </s> </s>", file=outfile)
    print("0 0 <unk> <unk>", file=outfile)
    print("0", file=outfile)

