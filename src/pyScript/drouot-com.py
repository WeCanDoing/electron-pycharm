# -*- coding: utf-8 -*-
import lxml
import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
import time
from sys import argv


catUrl = argv[1]
excelDownLoad = argv[2]
imgDownLoad = argv[3]
i = int(argv[4])
#是否只导出文本 0否 1是
onlyWrite =int(argv[5])
page = 0 

# 编号
lotNumber = []

# 起拍价
startPriceList = []

# 藏品名称
titles = []

# 描述
shortDescription = []

# 藏品地址
urlList = []

# 空填充
defaultList = []

# 设置要爬取的网页和保存的文件夹
folder = imgDownLoad
# 创建文件夹，如果已存在则跳过568个
if not os.path.exists(folder):
    os.mkdir(folder)

page = 1
sort = 0

#拼接url地址    
numbers = re.findall(r'\d+', catUrl)
venteId = numbers[0]

for i in range(i, page, 1):
    # 请求藏品
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    url = catUrl +"?offset=" + str(i) + "00&triSearch=num&venteId=" + str(venteId)
    with requests.get(url, headers=headers) as req:
        req.encoding = 'utf-8'
        html = req.content
    i = i + 1

    soup = BeautifulSoup(html, 'lxml')

    # 获取地址
    tags = soup.findAll('div', class_='product-cell margin-bottom-20')  # 获取class名为btn ghost primary的span节点

    for tag in tags:
        parent = tag.find_all('a')
        # 获取span节点的上级节点
        url = "https://drouot.com/" + parent[1].get('href')
        print("开始抓取" + url)

        urlList.append(url)
        with requests.get(url, headers=headers) as req:
            req.encoding = 'utf-8'
            detailHtml = req.content

        soup = BeautifulSoup(detailHtml, 'lxml')

        # 获取编号
        text = soup.find(class_="lotType font-red-d")
        text = text.find(class_="LisztFY-Bd")
        number = text.text.strip()
        lotNumber.append(number)
        defaultList.append("-")

        # 获取标题
        title = soup.find(class_="info_tps-prix-online")
        title = title.find(class_="noMarginBottom").get_text()
        title = str(title).strip()
        titles.append(title)


        # 获取描述
        element = soup.find(class_="descriptionLineWrap")
        description = element.get_text()
        shortDescription.append(description)

        # 获取起拍价
        if description == 'Non venu':
            startPriceList.append(0)
        else:
            context = soup.find(class_="infosLotEnchere")
            priceContext = context.find(class_="lineBpadding2")
            if priceContext is None:
                price = context.find(class_="font-dark-d floatRight").get_text()
                # pattern = r"\d+"
                # result = re.findall(pattern, price)
                # num = result[0] + "" + result[1]
                if price == 'Aucune estimation':
                    startPriceList.append(price)
                else:
                    num = price.strip().split("-")[0]
                    pattern = r"\d+"
                    num = re.findall(pattern, num)
                    result = int("".join(num))
                    startPriceList.append(result)
            else:
                price = priceContext.find(class_="floatRight").get_text()
                pattern = r"\d+"
                result = re.findall(pattern, price)
                num = int("".join(result))
                startPriceList.append(num)

        # 获取图片列表
        imgUrls = soup.findAll(class_="thumbPreview")
        num = 1

        # 存在图片只有一张封面图的情况
        if onlyWrite == 0:
            if imgUrls is None or len(imgUrls) == 0:
                divContext = soup.find(id='zoomImage')
                if divContext is None:
                    print("无效-不存图片，序号为", lotNumber[sort])
                else:
                    img = divContext.find("img")
                    src = img["src"]
                    src = src.replace("small", "fullHD")
                    print("图片", src)
                    # 写入图片
                    response = requests.get(src)
                    # 检查状态码，如果是200表示成功
                    if response.status_code == 200:
                        # 发送请求，获取图片的二进制数据
                        data = requests.get(src).content
                        # 拼接图片的路径和文件名
                        imul = str(lotNumber[sort]) + "-" + str(num) + ".jpg"
                        path = os.path.join(folder, imul.strip())
                        # 以二进制写入模式打开文件
                        with open(path, 'wb') as f:
                            # 将图片数据写入文件
                            f.write(data)
                            # 打印提示信息
                            print(f'已保存{src}到{path}')
                    else:
                        # 如果状态码不是200，打印错误信息
                        print(f'请求失败，状态码为{response.status_code}')
            else:
                for imgUrl in imgUrls:
                    style = imgUrl["style"]  # 获取style属性
                    pattern = r"url\('(.*)'\)"  # 匹配url('...')的模式
                    result = re.search(pattern, style)  # 返回一个match对象，包含匹配的结果

                    new_url = result.group(1).replace("small", "fullHD")

                    time.sleep(1)
                    # 写入图片

                    with requests.get(new_url) as response:
                        # 检查状态码，如果是200表示成功
                        if response.status_code == 200:
                            # 发送请求，获取图片的二进制数据
                            data = requests.get(new_url).content
                            # 拼接图片的路径和文件名
                            imul = str(lotNumber[sort]) + "-" + str(num) + ".jpg"
                            path = os.path.join(folder, imul.strip())
                            # 以二进制写入模式打开文件
                            with open(path, 'wb') as f:
                                # 将图片数据写入文件
                                f.write(data)
                                # 打印提示信息
                                print(f'已保存{new_url}到{path}')
                        else:
                            # 如果状态码不是200，打印错误信息
                            print(f'请求失败，状态码为{response.status_code}')
                        num = num + 1
        sort = sort + 1

# 创建一个DataFrame对象
dfData = {
    # 用字典设置DataFrame所需数据
    '图录编号': lotNumber,
    '藏品 名称': titles,
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

