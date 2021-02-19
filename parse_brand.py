from lxml import etree
with open(r'C:\Users\zhiku\PycharmProjects\untitled1\basic.txt', encoding='utf-8') as f:
    data = f.read()

html = etree.HTML(data)
# result = etree.tostring(html)
# brand_result = html.decode('utf-8')
div_list = html.xpath("/html/body/div[2]/div/div[2]/h1/text()")
print(div_list)

#0205:发送请求，获取响应
def parse_url(url):
    print(url)
    browser = webdriver.Chrome()
    try:
        browser.get(url)
        wait = WebDriverWait(browser, 10)
        # wait.until(EC.presence_of_element_located((By.ID,'content_left')))
        print(browser.current_url)
        print(browser.get_cookies())
        print(browser.page_source)
        browser.delete_all_cookies() #清除浏览器cookies
    finally:
        browser.close()

#0205：提取数据
def get_content_list(html_str): #提取数据
    html = etree.HTML(html_str)

    div_list = html.xpath("")  #根据div分组
    content_list = []
    for div in div_list:
        item = {}
        item['car_title'] = div.xpath()
        item['city'] = div.xpath()
        item['brand'] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()
        item[''] = div.xpath()

        city =
        brand =
        model =
        year_of_car =
        miles =
        box =
        gas =
        standard =
        lowest_price =
        round_price =
        owner_price =
        next_year_price =
        device =

# def brand_construct():
#     # for i in range(1,2000):
#     dic = {i:html.xpath('//a[@key={}]/text()'.format(str(i))) for i in range(1,2000)}
#         # index = str(i)
#         # dic[i] = html.xpath('//a[@key={}]/text()'.format(index))
#     return dic
#     # print(html.xpath('//a[@key="1"]/text()'))
#
# import pandas as pd
# lmm = brand_construct()
# # print(lmm)
# #字典转列表
# lis = []
# for i in lmm.keys():
#     lis.append(lmm[i])
# df = pd.DataFrame(data=lis)
# # df.head()
# df.to_excel('brand_id_04.xlsx')
