import requests
import re
from pymongo import MongoClient
client = MongoClient()
db = client.lagou
company_db = db.company


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/73.0.3683.86 Safari/537.36',
    'Host': 'www.lagou.com'
}

gongsi_id = 62

home_url = 'https://www.lagou.com/gongsi/j{id}.html'.format(id=gongsi_id)
home_resp = requests.get(home_url, headers=headers)
cookies = home_resp.cookies.get_dict()

headers['X_Anti_Forge_Token'] = re.search(r"window.X_Anti_Forge_Token = '(.*?)'", home_resp.text).group(1)
headers['X_Anti_Forge_Code'] = re.search(r"window.X_Anti_Forge_Code = '(.*?)'", home_resp.text).group(1)
headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
headers['Referer'] = home_url

postion_ajax = 'https://www.lagou.com/gongsi/searchPosition.json'
data = {
    'companyId': gongsi_id,
    'positionFirstType': '全部',
    'schoolJob': False,
    'pageNo': 1,
    'pageSize': 10
}
postions = requests.post(postion_ajax, data=data, headers=headers, cookies=cookies).json()
# company_db.insert_many(postions['content']['data']['page']['result'])
print(postions['content']['data']['page']['result'])