# -*- coding: utf-8 -*-
import os
import requests
import json
import jsonpath
import pandas as pd
from sys import argv

catUrl = argv[1]
excelDownLoad = argv[2]
imgDownLoad = argv[3]
page = int(argv[4])
#是否只导出文本 0否 1是
onlyWrite =int(argv[5])
pagesize = int(argv[4])

# 查询总条数
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

url = catUrl
urlCount = url + "&buyNow=false&keyword=&page=" + str(page) + "&pageSize=" + str(24) + "&sort=lotNumber"
req = requests.get(urlCount, headers=headers)
req.encoding = 'utf-8'

# json解析
resp_json = req.json()
# 获取最大条数
total = resp_json['payload']['totalRecords']

# 分页到达最大，查询所有数据
urlList = url + "&page=" + str(0) + "&pageSize=" + str(total) + "&sort=lotNumber"
reqList = requests.get(urlList, headers=headers)
reqList.encoding = 'utf-8'
result = json.loads(reqList.text)

# 解析json，获取具体数据
checkurlItem = "$.payload.items[*]"
object_list = jsonpath.jsonpath(result, checkurlItem)
print(object_list)

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

# 图片列表
imgList = []

# 设置要爬取的网页和保存的文件夹
folder = imgDownLoad

# 创建文件夹，如果已存在则跳过
if not os.path.exists(folder):
    os.mkdir(folder)

for i in object_list:
    lotNumber.append(i["lotNumber"])
    title.append(i["title"])
    shortDescription.append(i["shortDescription"])
    startPriceList.append(i["startPrice"])
    defaultList.append("-")
    url = "https://p1.liveauctioneers.com/" + str(i["sellerId"]) + "/" + str(i["catalogId"]) + "/" + str(
        i["itemId"]) + "_"
    if onlyWrite == 0:
        # 写入图片
        for phoneSort in i["photos"]:
            imgUrl = url + str(phoneSort) + "_x.jpg"
            # 获取网页内容
            response = requests.get(imgUrl)
            # 检查状态码，如果是200表示成功
            if response.status_code == 200:
                # 发送请求，获取图片的二进制数据
                data = requests.get(imgUrl).content
                # 拼接图片的路径和文件名
                path = os.path.join(folder, str(i["lotNumber"]) + "-" + str(phoneSort) + ".jpg")
                # 以二进制写入模式打开文件
                with open(path, 'wb') as f:
                    # 将图片数据写入文件
                    f.write(data)
                    # 打印提示信息
                    print(f'已保存{imgUrl}到{path}')
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
print(excelDownLoad + '已写入成功')


