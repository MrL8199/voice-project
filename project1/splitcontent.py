import os
from nltk.tokenize import sent_tokenize
fin = open("sample.txt","r")
lines = fin.readlines()
lines = ' '.join(lines)
lines = sent_tokenize(lines)

fout = open("sample_out.txt", "w")
for line in lines:
    fout.write(line + '\n')