import sys

alignment=open(sys.argv[1],"r").readlines()
alignment_reverse=open(sys.argv[2],"r").readlines()
alignment_combine=open(sys.argv[3],"w")

print len(alignment),len(alignment_reverse)

for i in range(len(alignment)):
	pairs=alignment[i].split()
	pairs_reverse=alignment_reverse[i].split()

	for pair in pairs:
		if str(pair.split("-")[1]+"-"+pair.split("-")[0]) in pairs_reverse:
			alignment_combine.write(pair+" ")
	alignment_combine.write("\n")
	



