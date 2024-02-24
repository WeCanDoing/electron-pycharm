import json
import os

import requests
import bs4
from bs4 import BeautifulSoup
import re
import pandas as pd
from sys import argv


# https://www.lot-art.com/外链到苏富比拍卖会(sothebys)的拍品抓取
# 取参数
catUrl = argv[1]
excelDownLoad = argv[2]
imgDownLoad = argv[3]
pageSize = argv[4]
page = 0 
if not page:
    page = 0

if not pageSize:
    pagesize = 1

# 编号
lotNumber = []

# 起拍价
startPriceList = []

# 藏品名称
title = []

# 描述
shortDescription = []

# 空填充
defaultList = []

# 查询总条数
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

url = "https://www.lot-art.com/api/security/login?_remember_me=1"
jsonData = {
    "motivator": "x",
    "email": "892045972@qq.com",
    "password": "xiongjian745",
    "_remember_me": "true"
}
req = requests.post(url, json=jsonData, headers=headers)
req.encoding = 'utf-8'
cookies = req.cookies
urlMenus = "https://www.lot-art.com/api/catalog/view"
menusJson = {"match_str":"00dea7147908eb9fccd01d817dff17ac","page":1,"cat":"","subcat":"","order":"sooner","q":"","need_catalog":1}


req = requests.post(urlMenus, cookies=cookies, headers=headers, json=menusJson)
req.encoding = 'utf-8'

# json解析
resp_json = req.json()
itemList = resp_json['items']

# 设置要爬取的网页和保存的文件夹
folder = imgDownLoad

# 创建文件夹，如果已存在则跳过
if not os.path.exists(folder):
    os.mkdir(folder)

# 获取信息
for item in itemList:
    lots = item["number"]
    lotNumber.append(lots)
    title.append(item["title"])
    startPriceList.append(item["low_estimate"])
    defaultList.append("-")
    match_str = item["match_str"]
    # 请求详情信息
    detailUrl = "https://www.lot-art.com/api/item/view"
    jsonData = {
        "match_str": match_str
    }

    req = requests.post(detailUrl, cookies=cookies, headers=headers, json=jsonData)
    req.encoding = 'utf-8'

    # json解析
    resp_json = req.json()
    shortDescription.append(resp_json['best_item']["description"])

    # 获得苏富比的拍品iD
    itemUrl = resp_json['best_item']['scrape_url']

    # 访问详情获取图片
    req = requests.get(itemUrl, headers=headers)
    req.encoding = 'utf-8'

    # 获取标题
    detailHtml = req.content
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(detailHtml, 'html.parser')

    # 找到 script 标签并获取内容
    script_tag = soup.find('script', id='__NEXT_DATA__')
    script_content = script_tag.string

    # 从 script 内容中移除第一行和最后一行（如果存在换行符的话）
    script_content = re.sub(r'\A\s+', '', script_content)
    script_content = re.sub(r'\s+\Z', '', script_content)

    # 将 script 内容解析为 JSON 对象
    json_obj = json.loads(script_content)

    # 从 JSON 对象中获取特定属性值
    ids = json_obj['props']['pageProps']['lot']['rowid']

    # 请求详情信息
    detailUrl = "https://live.bonhams.com/widget/lots/4-BQQSP2"
    jsonData = {"lot_ids": [ids]}

    req = requests.post(detailUrl, cookies=cookies, headers=headers, json=jsonData)
    req.encoding = 'utf-8'
    respDetail_json = req.json()
    items = respDetail_json['result_page']
    if len(items) > 0:
        itemList = items[0]['images']
        lot = 1
        for param in itemList:
            images = param['detail_url']

            # 获取网页内容
            response = requests.get(images)
            # 检查状态码，如果是200表示成功
            if response.status_code == 200:
                # 发送请求，获取图片的二进制数据
                data = requests.get(images).content
                # 拼接图片的路径和文件名

                print("下载第" + str(lot) + "张图片地址" + images)
                path = os.path.join(folder, str(lots) + "-" + str(lot) + ".jpg")
                # 以二进制写入模式打开文件
                with open(path, 'wb') as f:
                    # 将图片数据写入文件
                    f.write(data)
                    # 打印提示信息
                    print(f'已保存{images}到{path}')
                    lot = lot + 1
            else:
                # 如果状态码不是200，打印错误信息
                print(f'请求失败，状态码为{response.status_code}')

# 创建一个DataFrame对象
dfData = {
    # 用字典设置DataFrame所需数据
    '图录编号': lotNumber,
    '藏品名称': title,
    '品类': defaultList,
    '断代': defaultList,
    '品相': defaultList,
    '规格': defaultList,
    '描述': shortDescription,
    '起拍价': startPriceList,

}
df = pd.DataFrame(dfData)  # 创建DataFrame

# 将DataFrame对象写入到excel文件中
df.to_excel(excelDownLoad, index=False)



