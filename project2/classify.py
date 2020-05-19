import os
from shutil import copyfile
import xlrd
import math
import random
voice_data = []
for (paths, dirs, files) in os.walk("data/raw/."):
    for dirname in dirs:
        voice_data.append(dirname) # lấy các tên thư mục là mssv

# mở sheet phân loại từ
data_wb = xlrd.open_workbook("thongke.xlsx")

all_sheet = [data_wb.sheet_by_index(i) for i in range(1,6)] # [khong,nguoi,trong,cothe,duoc]
data_path = [ [], [], [], [], [] ]

for i in range(0,37):
    mssv = str(math.floor(all_sheet[0].cell_value(i,0)))
    if mssv in voice_data:
        for j in range(0,len(all_sheet)): # duyet lan luot cac sheet
            word_pos = int(all_sheet[j].cell_value(i,1))
            if (word_pos>2):
                for k in range(2,word_pos):
                    data_path[j].append(mssv + "/" + all_sheet[j].cell_value(i,k))
word_list = ["khong", "nguoi", "trong", "cothe", "duoc"]
word_list_pos = -1
for data_path_word in data_path:
    word_list_pos += 1
    random.shuffle(data_path_word)
    print("copying " + word_list[word_list_pos] + " ...")
    for i in range(0,100):
        src = "data/raw/" + data_path_word[i]
        dst = "data/classified/" + word_list[word_list_pos] + "/" + str(i) + ".wav"
        try:
            copyfile(src,dst)
        except:
            print("error: " + src + ", " + dst)
    print("done!")
#copyfile(src, dst)