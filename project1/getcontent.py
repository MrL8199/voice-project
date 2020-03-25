import framler
dt = framler.NewspapersParser("vnexpress")
url = "https://vnexpress.net/thoi-su/ha-tinh-to-chuc-cach-ly-tu-cap-xa-4074307.html"
article = dt.parse(url)
print(article.text)