# -*- coding: utf-8 -*-
__author__ = "ShiinaClariS"

'''
四川卫健委冠状病毒数据爬取
http://wsjkw.sc.gov.cn/scwsjkw/gzbd01/ztwzlmgl.shtml
'''

import re
import requests
from bs4 import BeautifulSoup

domain = "http://wsjkw.sc.gov.cn"
region = "四川"
page_count = 3


# 获取分页列表的地址列表
def get_all_data():
    all_data = []
    url_list = list(
        "http://wsjkw.sc.gov.cn/scwsjkw/gzbd01/ztwzlmgl_%d.shtml" % page for page in range(2, page_count + 1))
    url_list.insert(0, "http://wsjkw.sc.gov.cn/scwsjkw/gzbd01/ztwzlmgl.shtml")
    for url in url_list:
        all_data += get_news_list_page_data(url)
    print(all_data)
    return all_data


# 爬取新闻列表页面，获取当页所有新闻超链接
def get_news_list_page_data(url):
    print("visit: %s" % url)
    l = []
    r = requests.get(url)
    if r.status_code == 200:
        r.encoding = r.apparent_encoding
        # print(r.text);

        bs = BeautifulSoup(r.text, 'html.parser')
        li_list = bs.find(name="div", attrs={"class": "contMain fontSt"}).find_all(name="li")
        for li in li_list:
            da = li.findChildren(name="span", recursive=False)[0].get_text()
            url = domain + li.findChildren(name="a", recursive=False)[0].get("href")
            d = get_news_page_data(url)
            d["日期"] = da
            d["地区"] = region
            l.append(d)
    print(l)
    return l


# 爬取单个新闻页面数据，获得新闻段落
def get_news_page_data(url):
    d = {}
    r = requests.get(url)
    if r.status_code == 200:
        r.encoding = r.apparent_encoding
        # print(r.text);

        bs = BeautifulSoup(r.text, 'html.parser')
        span_list = bs.find_all(name="span", attrs={"style": "font-size: 12pt;"})
        for span in span_list:
            span_text = span.get_text()
            if span_text.__contains__("全省累计"):
                d = get_gzbd_data(span_text)
    return d


# 解析新闻数据
def get_gzbd_data(news_line):
    d = {}
    pattern = "全省累计报告新型冠状病毒肺炎确诊病例(\d+)例\(" \
              "其中境外输入(\d+)例\），累计治愈出院(\d+)例，" \
              "死亡(\d+)例，目前在院隔离治疗(\d+)例，(\d+)人尚在" \
              "接受医学观察"
    ma = re.search(pattern, news_line)
    if ma:
        d["确诊数"] = ma.group(1)
        d["输入数"] = ma.group(2)
        d["出院数"] = ma.group(3)
        d["死亡数"] = ma.group(4)
        d["治疗数"] = ma.group(5)
        d["观察数"] = ma.group(6)
    print(d)
    return d


if __name__ == "__main__":
    # news_line = "截至6月8日24时，全省累计报告新型冠状病毒肺炎确诊病例1043例(其中境外输入489例），累计治愈出院1009例，死亡3例，目前在院隔离治疗31例，364人尚在接受医学观察。"
    # get_gzbd_data(news_line);
    # url = "http://wsjkw.sc.gov.cn/scwsjkw/gzbd01/2021/6/9/4b58f2f87d294148a282f66b1a74f695.shtml";
    # get_news_page_data(url);
    # url = "http://wsjkw.sc.gov.cn/scwsjkw/gzbd01/ztwzlmgl_2.shtml";
    # get_news_list_page_data(url);
    get_all_data()
