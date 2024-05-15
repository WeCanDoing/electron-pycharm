import requests
from bs4 import BeautifulSoup
import pandas as pd
import textwrap
import os
from sys import argv


catUrl = argv[1]
excelDownLoad = argv[2]
imgDownLoad = argv[3]
i = int(argv[4])
#是否只导出文本 0否 1是
onlyWrite =int(argv[5])

# 抓取www.the-saleroom.comt网站
# 抓取页码知道请求多少页
# 编号
lotNumber = []

# 起拍价
startPriceList = []

# 藏品名称
titles = []

# 描述
shortDescription = []

# 规格
attrs = []

# 藏品地址
urlList = []

# 空填充
defaultList = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

url = catUrl

headers = {"Content-Type": "application/x-www-form-urlencoded"}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

html = response.content

soup = BeautifulSoup(html, 'lxml')
s = requests.session()
s.keep_alive = False  # 关闭多余连接
s.get(url)  # 你需要的网址
text = soup.select(".pagination-content")

# 设置要爬取的网页和保存的文件夹
folder = imgDownLoad
# 创建文件夹，如果已存在则跳过
if not os.path.exists(folder):
    os.mkdir(folder)

pagesSize = 1
for ul in text:
    pagesSize = int(ul.get("data-pages"))
i = i + 1
while i <= pagesSize:
    pageUrl = url + "?page=" + str(i)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.get(pageUrl, headers=headers)
    response.encoding = 'utf-8'
    i = i + 1

    html = response.content

    soup = BeautifulSoup(html, 'lxml')
    soup = soup.select(".lot-listing-results")
    detail = soup[0].select(".lot-single  ")
    for dto in detail:

        # 填充空白
        defaultList.append("-")

        # 标题
        title = dto.find("span", class_="lot-title").get_text()
        print(title)
        titles.append(title)

        # 价格
        span = dto.find("span", class_="lot-details-subtitle-text")
        text = span.get_text()
        price = text.split()[0]  # 这一行是我添加的代码，表示按空格分割文本，并取出第一个元素
        print(price)
        startPriceList.append(price)

        # 编号
        span = dto.find("span", class_="lot-number")
        text = span.get_text()
        number = text.split()[0]  # 这一行是我添加的代码，表示按空格分割文本，并取出第一个元素
        print(number)
        lotNumber.append(number)

        # 查询详情获取图片和描述
        value = dto.get("id")
        detailUrl = url + "/" + value
        print(detailUrl)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.get(detailUrl, headers=headers)
        response.encoding = 'utf-8'

        html = response.content

        soup = BeautifulSoup(html, 'lxml')
        description = soup.find("div", class_="twelve wide mobile only column accordion-wrapper")
        description = description.select(".content")
        var = description[0]
        # 找到所有的 div 標籤，並選擇第二個（索引為 1）
        divs = var.find_all("div")
        div = divs[0]

        # 找到 div 標籤中的所有文本，並去除空白字符
        text = div.get_text(strip=True)

        # 分割文本，並選擇第二個（索引為 1），即中文那段的所有內容
        parts = text.split("\n")
        chinese = parts[0]
        description = textwrap.shorten(chinese, 1000)
        # 添加描述
        shortDescription.append(description)

        # 添加图片
        if onlyWrite == 0:
            indexImages = soup.find("div", class_="lot-details-image slider")
            indexImages.find("div", class_="image")
            indexImage = indexImages.find("img")
            print(indexImage)
            indexAlt = indexImage.get("alt")
            if indexAlt != "No Image" :
                indexImageUrl = indexImage.get("data-lazy")
                index = 1
                imgUrl = indexImageUrl.split('?')[0]
               # 获取网页内容
                response = requests.get(imgUrl)
                # 检查状态码，如果是200表示成功
                if response.status_code == 200:
                    # 发送请求，获取图片的二进制数据
                    data = requests.get(imgUrl).content
                    # 拼接图片的路径和文件名
                    path = os.path.join(folder, str(number) + "-" + str(index) + ".jpg")
                    # 以二进制写入模式打开文件
                    with open(path, 'wb') as f:
                        # 将图片数据写入文件
                        f.write(data)
                        # 打印提示信息
                        print(f'已保存{imgUrl}到{path}')
                        index = index + 1
                else:
                    # 如果状态码不是200，打印错误信息
                    print(f'请求失败，状态码为{response.status_code}')

                imgDtos = indexImages.find_all("div", class_="extra-images image")

                for imgDiv in imgDtos:
                    indexImages = imgDiv.find("img")
                    imgUrl = indexImages.get("data-lazy")
                    imgUrl = imgUrl.split('?')[0]
                    # 发送请求，获取图片的二进制数据
                    data = requests.get(imgUrl).content
                    # 拼接图片的路径和文件名
                    path = os.path.join(folder, str(number) + "-" + str(index) + ".jpg")
                    # 以二进制写入模式打开文件
                    with open(path, 'wb') as f:
                        # 将图片数据写入文件
                        f.write(data)
                        # 打印提示信息
                        print(f'已保存{imgUrl}到{path}')
                        index = index + 1
                else:
                    # 如果状态码不是200，打印错误信息
                    print(f'请求失败，状态码为{response.status_code}')

# 创建一个DataFrame对象
dfData = {
    # 用字典设置DataFrame所需数据
    '图录编号': lotNumber,
    '藏品名称': titles,
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


