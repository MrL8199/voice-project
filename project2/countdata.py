import xlrd
from underthesea import word_tokenize
import string

# lay noi dung bai bao trong cell
def cellToSentences(cell_value):
    sentences = ""
    data = cell_value.split("\n")
    for i in range(2, len(data)):
        if (i % 2 == 0):
            sentences = sentences + data[i] + "\n"
    return sentences


def countWordInSentences(sentences):
    counter = dict()
    allword = word_tokenize(sentences)
    for word in allword:
        if word not in string.punctuation:
            if (counter.get(word) is None):
                counter[word] = 1
            else:
                counter[word] += 1
    return counter


# open work book
wb = xlrd.open_workbook("data.xlsx")
sheet = wb.sheet_by_index(2)  # chon sheet thu 3 (assignment-2)

sentences = ""
# duyet het sinh vien
for i in range(1, 38):
    for j in range(3, 18):  # duyet tat ca cac  chu de
        sentences = sentences + cellToSentences(sheet.cell_value(i, j)) + "\n"

counter = countWordInSentences(sentences)  # dem so lan xuat hien cua cac tu

counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)

f = open("count.txt", "a", encoding="utf-8")
for c in counter:
    print(c)
    f.write(c[0] + ":" + str(c[1]) + "\n")
f.close()
