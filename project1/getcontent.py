import framler
import os
from underthesea import sent_tokenize

dt = framler.NewspapersParser("vnexpress")
with open("links.txt", "r") as f:
    urls = f.readlines()
for url in urls:
    article = dt.parse(url)
    # url.split("/")[3] trả về loại bài báo
    directory_save = "data/" + url.split("/")[3]
    # nếu folder chưa tồn tại thì tạo mới
    if not os.path.exists(directory_save):
        os.makedirs(directory_save,exist_ok=True)
    sentences = sent_tokenize(article.text)
    f = open(directory_save + "/" +"data.txt","w",encoding='utf-8')
    for sentence in sentences:
        f.write(sentence+ "\n")
    f.close()