import framler
import re
import os
import feedparser
dt = framler.NewspapersParser("vnexpress")
while True:
    rss_url = input("Link RSS: ")
    feed = feedparser.parse(rss_url)
    items = feed["items"]
    for item in items:
        url = item["link"]
        article = dt.parse(url)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', article.text)
        # url.split("/")[3] trả về loại bài báo
        directory_save = "data/" + url.split("/")[3]
        # nếu folder chưa tồn tại thì tạo mới
        if not os.path.exists(directory_save):
            os.makedirs(directory_save,exist_ok=True)
        # tách thành các câu
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', article.text)
        print("Num sentences: " , len(sentences))
        
        if(len(sentences) >= 14 and len(sentences) < 20):
            # ghi các câu này thành dữ liệu
            f = open(directory_save + "/" +"data.txt","w",encoding='utf-8')
            # ghi url vào dòng đầu
            f.write(url+"\n")
            for sentence in sentences:
                f.write(sentence+ "\n")
            f.close()
            print("Saved")
            print(url)
            break