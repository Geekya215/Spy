import requests
import re
from bs4 import BeautifulSoup
import jieba
import wordcloud

# 26654184
home_url_prefix = "https://movie.douban.com/subject/"
review_url_prefix = "https://movie.douban.com/review/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47"}
reviews = []


def generate_home_url(sid):
    return home_url_prefix + sid


def get_movie_information(sid):
    bs = BeautifulSoup(requests.get(url=generate_home_url(sid), headers=headers), "lxml")
    title = bs.find('span', {"property": "v:itemreviewed"}).string
    year = bs.find('span', {"class": "year"}).string[1:-1]
    movie_class = bs.findAll('span', property="v:genre")
    score = bs.find('strong', {"property": "v:average"}).string
    try:
        votes = bs.find('span', property="v:votes").string
    except Exception:
        votes = ''
        pass
    try:
        time = bs.find('span', {"property": "v:runtime"}).string
    except Exception:
        time = 0
        pass
    classes = ''
    for item in movie_class:
        classes = item.string + " " + classes
    try:
        summary = bs.find('span', property="v:summary")
        p = re.compile(r"<.+>")
        q = re.compile(r"[\n　]")
        summary = p.sub('', str(summary))
        summary = q.sub('', summary)
        summary = summary.replace(' ', '').strip().strip('\n')
    except Exception:
        summary = ' '
        pass
    info = [title, year, classes, time, score, votes, summary]
    return info


def get_reviews(sid):
    for i in range(0, 140, 20):
        reviews_list_url = f"{generate_home_url(sid)}reviews?start={i}"
        reviews_list = BeautifulSoup(requests.get(url=reviews_list_url, headers=headers).content, "lxml").findAll('div', attrs={"data-cid": re.compile("\d")})
        for review in reviews_list:
            review_url = f"{review_url_prefix}{review['data-cid']}"
            review_body = BeautifulSoup(requests.get(url=review_url, headers=headers).content, "lxml").find("div", attrs={"class": "review-content clearfix"})
            review_content = ""
            for p in review_body.find_all('p'):
                review_content += p.text + "\n"
            reviews.append(review_content)


def save_reviews():
    with open("reviews.txt", "w", encoding="utf-8") as f:
        for review in reviews:
            f.write(review)


def word_split():
    with open("reviews.txt", "r", encoding="utf-8") as f:
        return " ".join(jieba.lcut(f.read()))


def wordcloud_generate():
    w = wordcloud.WordCloud(
        font_path="msyh.ttc",
        width=1000,
        height=700,
        background_color="white"
    )
    w.generate(word_split())
    w.to_file("reviews.png")