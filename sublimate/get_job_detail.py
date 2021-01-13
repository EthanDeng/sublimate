from exusiai import xpath, findall, xstrip, requests_get
from datetime import datetime
from lxml import etree
import pandas as pd

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
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
    return job_detail_dict


job_list = ['https://sh.58.com/tech/38582462481939x.shtml',
            'https://sh.58.com/siji/42779505522968x.shtml',
            'https://sh.58.com/zhaopin/38140143168532x.shtml']


def main():
    for index, job in enumerate(job_list):
        print("正在爬取第", index, "个招聘信息", "招聘网址为：", job)
        job_detail = parse_detail(job)
        job_detail_df = pd.DataFrame.from_records([job_detail])
        write_mode = 'w' if index == 0 else 'a'
        header_tf = True if index == 0 else False
        job_detail_df.to_csv('job_detail.csv', mode=write_mode, encoding='gb2312', header=header_tf)
        print("第", index, "个详情信息写入完毕...")


if __name__ == '__main__':
    main()

