import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from sys import argv

catUrl = argv[1]
excelDownLoad = argv[2]
imgDownLoad = argv[3]
i = int(argv[4])
# 是否只导出文本 0否 1是
onlyWrite = int(argv[5])

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

# 估价
normalPrice = []

# 设置要爬取的网页和保存的文件夹
folder = imgDownLoad
# 创建文件夹，如果已存在则跳过
if not os.path.exists(folder):
    os.mkdir(folder)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

url = catUrl
s = requests.session()
s.keep_alive = False  # 关闭多余连接
response = s.get(url)
response.encoding = 'utf-8'

# 查询分页
html = response.content
soup = BeautifulSoup(html, 'lxml')
page_div = soup.find('div', class_='page')
links = page_div.find_all('a')
last_page_number = 1
for link in links:
    pageNumber = link.text.replace("..", "")
    if pageNumber.strip().isdigit():
        last_page_number = int(pageNumber.strip())

# 分页调用，请求每个对应分页的数据
while int(i) < last_page_number:
    i = i + 1
    url = url.replace(".html", "")
    pageUrl = url + "/p/" + str(i) + ".html"
    response = requests.get(pageUrl)
    response.encoding = 'utf-8'

    html = response.content

    soup = BeautifulSoup(html, 'lxml')
    detail = soup.findAll('li', class_='lots_pic')
    for dto in detail:

        # 填充空白
        defaultList.append("-")

        # 标题
        title = dto.find('div', class_='name').text
        print(title)
        titles.append(title)

        # 价格 和 编号
        try:
            span = dto.find("div", class_="info")
            span = span.find_all('p')
            text = span[0].get_text()
            number = text.replace("图录号：", "")  # 这一行是我添加的代码，表示按空格分割文本，并取出第一个元素
            lotNumber.append(number)

            # 估价和价格
            price = span[1].get_text()  # 这一行是我添加的代码，表示按空格分割文本，并取出第一个元素
            normalPrice.append(price)

            price = price.replace("估价RMB:", "").strip()  # 这一行是我添加的代码，表示按空格分割文本，并取出第一个元素
            startPriceList.append(price)

        except AttributeError:
            startPriceList.append(0)
            lotNumber.append("读取失败")
            normalPrice.append("读取失败")

        detailUrl = dto.find('a', class_='clearfix')
        href_link = detailUrl['href']

        # 查询详情获取图片和描述
        detailUrl = "http://www.xlysauc.com/" + href_link
        response = requests.get(detailUrl)
        response.encoding = 'utf-8'

        html = response.content

        soup = BeautifulSoup(html, 'lxml')
        description = soup.find("div", class_="txt swiper-no-swiping")
        # 添加描述
        text_with_newlines = description.decode_contents().replace('<br/>', '\n').strip()
        shortDescription.append(text_with_newlines)

        # 添加图片
        if onlyWrite == 0:
            indexImages = dto.find("div", class_="pic")
            img_tag = indexImages.find('img')
            # 获取src属性的值
            src_value = img_tag['src']
            src_value = src_value.replace("?x-oss-process=style/lots_cover", "")
            print(src_value)
            # 获取网页内容
            response = requests.get(src_value)
            # 检查状态码，如果是200表示成功
            if response.status_code == 200:
                # 发送请求，获取图片的二进制数据
                data = requests.get(src_value).content
                # 拼接图片的路径和文件名
                path = os.path.join(folder, str(number) + "-1.jpg")
                # 以二进制写入模式打开文件
                with open(path, 'wb') as f:
                    # 将图片数据写入文件
                    f.write(data)
                    # 打印提示信息
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
    '估价': normalPrice

}
df = pd.DataFrame(dfData)  # 创建DataFrame

# 将DataFrame对象写入到excel文件中
df.to_excel(excelDownLoad, index=False)
