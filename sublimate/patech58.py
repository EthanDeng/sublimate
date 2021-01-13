import requests
from lxml import etree
import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import re
import time
import json
from multiprocessing.dummy import Pool as ThreadPool
import json
from exusiai import xpath, findall, xstrip, requests_get
import requests
from retrying import retry
from fake_useragent import UserAgent
import random
ua = UserAgent()
client = MongoClient()
db = client.city58
city_db = db.city_list
industry_db = db.industry_urls

company_db = db.company_list
jobs_urls = db.job_urls
jobs_db = db.job_detail2
company_info_db = db.company_info

hot_city = ['北京', '成都', '长沙', '广州', '杭州', '济南', '上海', '深圳', '苏州', '天津', '武汉']

city_list = pd.DataFrame(list(city_db.find()))
city_dict = dict(zip(city_list['城市'], city_list['城市网址']))


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7",
    "cache-control": "max-age=0",
    "dnt": "1",
    "referer": "https://sh.58.com/job.shtml?PGTID=0d100000-0000-2830-f73b-cb30d46ed0cf&ClickID=2",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "Connection": "keep-alive",
    "upgrade-insecure-requests": "1"}


def gen_ip_info(proxy_list):
    base_dict = {
        "req_date": datetime.now(),
        "last_fail": None,
        "last_use": None
    }
    ip_info = dict.fromkeys(proxy_list, base_dict)
    return ip_info


def req_url(city, query_dict=None):
    if query_dict is None:
        query_dict = city_dict
    city_sn = query_dict[city].split('/')[-2]
    city_url = 'https://%s.58.com/job.shtml' % city_sn
    return city_url


def get_proxy(ip_num=1):
    proxy_json = requests.get('http://proxyip.com' % ip_num).json()
    all_proxy = []
    for item in proxy_json['data']:
        ip = item['ip']
        port = item['port']
        proxy = "%s:%s" % (ip, port)
        all_proxy.append(proxy)
    return ['58.218.92.177:8315']





def crawl_industry(city_url):
    response = requests_get(city_url)
    html = etree.HTML(response.content)
    industry_list = html.xpath("//ul[@class='indcatelist']/li/a/text()")
    industry_url = [city_url[:-6] + item for item in html.xpath("//ul[@class='indcatelist']/li/a/@href")]
    industry_df = pd.DataFrame(list(zip(industry_list, industry_url)), columns=['行业', '行业网址'])
    industry_df = industry_df.query('行业 != "不限"').reset_index(drop=True)
    industry_df['city_url'] = city_url
    industry_db.insert_many(industry_df.to_dict('records'))


def industry_by_area(industry_url):
    response = requests_get(industry_url)
    html = etree.HTML(response.content)
    area = html.xpath('//div[@class="filter_item filter_area"]/ul[@class="filter_items clearfix"]/li/a/text()')
    area_url = html.xpath('//div[@class="filter_item filter_area"]/ul[@class="filter_items clearfix"]/li/a/@href')
    area_df = pd.DataFrame(list(zip(area[1:], area_url[1:])), columns=['行政区', '行业网址'])
    industry_db.insert_many(area_df.to_dict('records'))


def total_pages(industry_url):
    response = requests_get(industry_url)
    html = etree.HTML(response.content)
    # total_counts = int(html.xpath("//span[@class='operate_txt']/i/text()")[0])
    total_pn = int(html.xpath("//span[@class='num_operate']/i[@class='total_page']/text()")[0])
    return total_pn


def crawl_jobs(page_url):
    # page_url = 'https://sh.58.com/job/pn1/pve_5363_253_pve_5358_0/'
    response = requests_get(page_url)
    html = etree.HTML(response.content)
    total_page = int(html.xpath('//span[@class="total_page"]/text()'))
    jobs_url = html.xpath("//div[@class='job_name clearfix']/a/@href")
    jobs_url = [job_url.split('?')[0] for job_url in jobs_url if not job_url.startswith('https://legoclick')]
    jobs_df = pd.DataFrame(jobs_url, columns=["job_url"])
    jobs_df['page_url'] = page_url
    jobs_urls.insert_many(jobs_df.to_dict('records'))
    print(page_url, '完成爬取...')
    return total_page


def crawl_industry_jobs(ind_url):
    page = 1
    total_page = 1
    while page <= total_page:
        x0, x1 = ind_url.split('job/')
        page_url = x0 + 'job/pn' + str(page) + '/' + x1
        page = page + 1
        total_page = crawl_jobs(page_url)
        print(page, total_page)


def parse_detail(job_url):
    response = requests_get(job_url, headers=HEADERS)
    code = response.status_code
    job_detail_dict = {
        "job_url": job_url,
        "status_code": code,
        "scrape_date": datetime.today().strftime('%Y/%m/%d')}
    if code == 200:
        doc = response.text
        html = etree.HTML(response.text)
        pub_date = findall('"pubDate":(.*?)"upDate"', doc)
        lontitude = findall('"lon":"(.*?)"', doc)
        latitude = findall('"lat":"(.*?)"}', doc)
        update_date = findall('"upDate":(.*?)}', doc)
        pos_title = xpath('//span[@class="pos_title"]/text()', html)
        pos_name = xpath('//span[@class="pos_name"]/text()', html)
        pos_salary = xpath('//span[@class="pos_salary"]/text()', html)
        pos_welfare = '、'.join(xpath('//span[@class="pos_welfare_item"]/text()', html, first=False))
        pos_condition = '、'.join(xpath('//div[@class="pos_base_condition"]/span/text()', html, first=False))
        pos_area = '-'.join(xpath('//span[@class="pos_area_item"]/text()', html, first=False))
        pos_address = xpath('//div[@class="pos-area"]/span[2]/text()', html)
        pos_description = xpath('//div[@class="des"]', html, first=False, child=True)
        company_name = xpath('//div[@class="baseInfo_link"]/a/text()', html)
        company_url = xpath('//div[@class="baseInfo_link"]/a/@href', html)
        title_sign = xpath('//span[@class="baseInfo_sign"]/i/@title', html)
        company_industry = xpath('//p[@class="comp_baseInfo_belong"]/a/text()', html)
        company_scale = xpath('//p[@class="comp_baseInfo_scale"]/text()', html)
        job_offers = xpath('//a[@class="look_pos"]/@href', html)
        job_detail_dict.update({
            "pub_date": pub_date,
            "update_date": update_date,
            "lontitude": lontitude,
            "latitude": latitude,
            "pos_title": pos_title,
            "pos_name": pos_name,
            "pos_salary": pos_salary,
            "pos_welfare": pos_welfare,
            "pos_condition": pos_condition,
            "pos_area": pos_area,
            "pos_address": pos_address,
            "pos_description": pos_description,
            "company_name": company_name,
            "company_url": company_url,
            "title_sign": title_sign,
            "company_industry": company_industry,
            "company_scale": company_scale,
            "job_offers": job_offers,
        })
        print(job_detail_dict)
    # jobs_db.insert_one(job_detail_dict)


def main():
    # ind_url = 'https://sh.58.com/job/pve_5358_0_pve_5363_247/'
    # crawl_industry_jobs(ind_url=ind_url)
    # industry_by_area('https://sh.58.com/job/pve_5358_0_pve_5363_255/')
    # industry_df = pd.DataFrame(list(industry_db.find())).query('行政区 in ["金山", "崇明", "上海周边"]')
    # for index, row in industry_df.iterrows():
    #     area = row['行政区']
    #     area_url = row['行业网址']
    #     crawl_industry_jobs(ind_url=area_url)
    #     print(area, "写入到 MongoDB 中..")

    job_list = list(pd.DataFrame(list(jobs_urls.find()))['job_url'])
    exist_df = pd.DataFrame(list(jobs_db.find()))
    if 'job_url' not in exist_df.columns.tolist():
        exist = []
    else:
        exist = list(exist_df['job_url'])
    missing = list(set(job_list) - set(exist))
    print(missing)
    for job in missing:
        job = 'https://sh.58.com/zpshengchankaifa/42940719553676x.shtml'
        parse_detail(job)
        exit()

    # tpn = total_pages('https://sh.58.com/pudongxinqu/job/pve_5358_0_pve_5363_255/')
    # print(tpn)
    # parse_detail()


if __name__ == '__main__':
    main()
