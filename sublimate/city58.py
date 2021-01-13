import requests
from lxml import etree
import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import date
from multiprocessing.dummy import Pool as ThreadPool
import json
client = MongoClient()
db = client.city58
city_db = db.city_list
city_industry_db = db.city_industry_list

company_db = db.company_list
job_db = db.job_list
company_info_db = db.company_info

hot_city = ['北京', '成都', '长沙', '广州', '杭州', '济南', '上海', '深圳', '苏州', '天津', '武汉']


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
}

table_headers = ['职位信息', '薪资水平', '工作地点', '学历', '工作经验', '招聘人数', '更新时间']


def crawl_city(url=None):
    url = 'https://qy.58.com/citylist/'
    response = requests.get(url=url, headers=headers).content
    html = etree.HTML(response)
    city_list = html.xpath("//dl[@id='clist']/dd/a/text()")
    city_url = ['https:' + item for item in html.xpath("//dl[@id='clist']/dd/a/@href")]
    city_df = pd.DataFrame(list(zip(city_list, city_url)), columns=['城市', '城市网址'])
    city_db.insert_many(city_df.to_dict('records'))


def crawl_industry(city, city_url):
    response = requests.get(url=city_url, headers=headers).content
    html = etree.HTML(response)
    industry_list = html.xpath("//dl[@class='selIndCate']/dd/span/a/text()")
    industry_url = ['https:' + item for item in html.xpath("//dl[@class='selIndCate']/dd/span/a/@href")]
    industry_df = pd.DataFrame(list(zip(industry_list, industry_url)), columns=['行业', '行业网址'])
    industry_df = industry_df.query('行业 != "全部"').reset_index(drop=True)
    industry_df['城市'] = city
    industry_df['城市网址'] = city_url
    city_industry_db.insert_many(industry_df.to_dict('records'))


def crawl_companies(page=1):
    industry_url = 'https://qy.58.com/nj_255/pn%s' % page
    response = requests.get(url=industry_url, headers=headers).content
    html = etree.HTML(response)
    company_list = html.xpath("//div[@class='compList']/ul/li/span/a/text()")
    company_url = ['https:' + item for item in html.xpath("//div[@class='compList']/ul/li/span/a/@href")]
    company_df = pd.DataFrame(list(zip(company_list, company_url)), columns=['company', 'company_url'])
    if not len(company_list):
        print("第 %s 页爬取失败...重新爬取中..." % page)
        crawl_companies(page)
    else:
        print("第 %s 页完成爬取...数据导出中..." % page)
        company_df['page'] = page
        company_df['url'] = industry_url
        if page == 1:
            company_df.to_csv('company_df.csv', index=False, mode='w', header=True)
        else:
            company_df.to_csv('company_df.csv', index=False, mode='a', header=False)
        page = page + 1
        if page < 78:
            crawl_companies(page)


def parse_jobs_panel(company=None, company_url=None):
    # company = '南京壮壮贸易有限公司'
    # company_url = 'https://qy.58.com/60552022020368/'  # 无数据公司
    # company_url = 'https://qy.58.com/60574999503620/'  # 有数据公司
    response = requests.get(company_url, headers=headers, allow_redirects=False).content
    if response:
        html = etree.HTML(response)
        job_urls = html.xpath("//a[@class='j_table_c']/@href")
        print(job_urls)
        job_content = html.xpath("//a[@class='j_table_c']")
        job_nan = html.xpath("//div[@class='j_table_c']/text()")[0]
        jobs_df = pd.DataFrame(columns=table_headers)
        if len(job_content) > 0:
            print('%s（%s）有招聘历史数据...' % (company, company_url))

            for item in job_content:
                job_info = [''.join(dd.itertext()).strip().replace('\n', '、') for dd in item.xpath('./span')]
                job_df = pd.DataFrame(np.array(job_info).reshape(-1, len(job_info)))
                if jobs_df.shape[0] == 0:
                    jobs_df = job_df
                else:
                    jobs_df = pd.concat([jobs_df, job_df])
            jobs_df.columns = table_headers
            jobs_df['招聘网址'] = job_urls
        elif job_nan == '暂无全职职位信息':
            print('%s %s 没有招聘历史数据...' % (company, company_url))
            jobs_df['职位信息'] = ['无']
        jobs_df['公司'] = company
        jobs_df['公司网址'] = company_url
        jobs_df['获取时间'] = date.today().strftime("%Y/%m/%d")
        jobs_df = jobs_df.filter(['公司', '公司网址'] + table_headers + ['招聘网址', '获取时间'])
        job_db.insert_many(jobs_df.to_dict('records'))
        print(company, company_url, "招聘信息爬取完毕...")


def parse_company_jobs():
    companies = pd.read_excel('南京批发零售企业名单.xlsx', sheet_name='company_df')
    for index, row in companies.iterrows():
        company = row['company']
        company_url = row['company_url']
        print('No.', index, company, company_url, '开始爬取...')
        parse_jobs_panel(company=company, company_url=company_url)


def main():
    # crawl_city()
    data = pd.DataFrame(list(city_db.find()))
    for index, row in data.iterrows():
        city = row['城市']
        city_url = row['城市网址']
        print(city, city_url)
        try:
            crawl_industry(city, city_url)
        except:
            try:
                crawl_industry(city, city_url)
            except:
                try:
                    crawl_industry(city, city_url)
                except:
                    pass
    # city_url = city_df.query('城市 == "南京"')['城市网址'].reset_index(drop=True)[0]
    # crawl_industry('南京', city_url)
    # crawl_industries()
    # crawl_companies()
    # parse_company_jobs()
    # parse_company_jobs()
    # parse_jobs_panel()


if __name__ == '__main__':
    main()
