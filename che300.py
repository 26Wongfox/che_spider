#! /usr/bin/env python
#-*-coding:utf-8-*

#导包
import random, time, csv, os, requests, json
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

primary_url = "https://www.che300.com/buycar/"
#把url抽离出来
def make_url(city, brand, page):
    base_url = "https://www.che300.com/buycar/"
    city_id = "&city={}".format(city)
    brand_id = "b{}v1c1?".format(brand)
    page_id = "p={}".format(page * 20)  #设置翻页
    url = base_url + brand_id + page_id + city_id
    return url

#构造城市+品牌组合
def city_brand(file_path):
    # import json
    # 读取城市和品牌的json文件，然后拼接成列表or元组
    # id_path = file_path
    with open(file_path, 'r', encoding='utf-8') as file:
        file_json = json.load(file)
        item_key = "id" if "brand" in file_path else "city_id"
        file_list = [int(file_json[i][item_key]) for i in range(len(file_json))]
    return file_list

#另一种思路：每次循环页面，都先获取页面结果，如果是【很抱歉暂时没有发现您要找的车】，就打印【没有车】，然后结束本次循环，跳转到下一个城市+品牌的搜索请求
def get_response(url): #请求页面并获取源码
    print("开始请求页面url")
    browser = webdriver.Chrome()
    browser.get(url)
    browser.set_page_load_timeout(10) #页面加载超时等待时间
    browser.delete_all_cookies() #请求后即可清空cookies
    page_source = browser.page_source
    html = etree.HTML(page_source)
    page_result = html.xpath("/html/body/div[3]/div/p/text()") #获取搜索结果的情况。可能为空
    time.sleep(random.randint(1,3)) #随机延时1-3秒
    # browser.close()  #关闭浏览器
    #返回两个值：源码，是否有页面
    return html, page_result

#解析内容，获取字段
def parse_html(html):
    # 提前构造二手车信息的xpath
    print("开始解析页面")
    # list_index = [[i,j] for i in range(1,6) for j in range(1,5)] #页面是5行4列，构造一个数组
    # for i in list_index:
    #     title = html.xpath("/html/body/div[4]/div[1]/ul[{}]/li[{}]/div/a/p/text()".format(i[0], i[1]))
    #     info = html.xpath("/html/body/div[4]/div[1]/ul[{}]/li[{}]/div/p[1]/a[1]/text()".format(i[0], i[1]))
    #     source = html.xpath("/html/body/div[4]/div[1]/ul[{}]/li[{}]/div/p[1]/a[2]/text()".format(i[0], i[1]))
    #     price = html.xpath("/html/body/div[4]/div[1]/ul[1]/li[2]/div/p[2]/span/i/text()".format(i[0], i[1]))
    #     gap_price = html.xpath("/html/body/div[4]/div[1]/ul[{}]/li[{}]/div/p[3]/span[1]/i/text()".format(i[0], i[1]))

    #页面结果不一致，可能一页不满足5行4列的情况。更换解析的方式：class
    title = html.xpath('//p[@class="list-title"]/text()')
    info = html.xpath('//p/a[contains(@href, "che300.com/buycar") and @target="_blank"]/text()')
    source = html.xpath('//a[@style="text-decoration: underline;"]/text()')
    price = html.xpath('//span[@class="list-price"]/i/text()')
    gap_price = html.xpath('//i[@class="high" or @class="low"]/text()')
    print("标题", title, "信息", info, "来源", source, "价格", price, "差价", gap_price)
    return title, info, source, price, gap_price

#定义个合并列表的函数
def construct_list(a,b,d,e,f):
    c = a + b
    c.append(d)
    c.append(e)
    c.append(f)
    yield c
    
#处理解析后得到的初始字段
def split_field(title, info, source, price, gap_price):
    null_list = []
    # title_list = [i for i in  title[0].split(' ')]  #解析标题：年款/品牌/排量/车型
    title_list = title
    info_list = [' '.join(i.split('/')) for i in info]  #解析：上牌日期/公里数/城市
    # info_list[2] = float(info_list[2][:-3]) #把公里数转换成浮点数值
    price_float = [float(i) for i in price] #把价格转换成浮点数值
    high_or_low = [(i[0]) for i in gap_price]
    gap_price_float = [float(i[1:-1]) for i in gap_price]
    for i in range(len(title)):
        title_info = title_list[i] + ',,' + info_list[i] + ',,' + str(price_float[i]) + ',,' + high_or_low[i] + ',,' + str(gap_price_float[i])
    null_list.append(title_info.split(',,'))
    print("处理后的字段：", null_list)
    print("信息字段",info_list)
    return null_list  #把所有解析好的字段作为一个列表返回


# 意外解决：如中途中断，记录下已请求的网页链接和待请求的
# def urls_save(filename, total_urls):
#     # 已请求的URL
#     requested_url = [].append(url)
#     requested_url_set = set(requested_url)
#     total_urls_set = set(total_urls)
#     #没有结果的页面URL
#     zero_result_url = [url]
#     # 待请求URL,差集
#     request_url_null = total_urls_set - requested_url_set
#     with open(filename, mode='a') as csv_file:
#         writer = csv.writer(csv_file)
#         for url in request_url_null:
#             writer.writerow(url)
#         print("已保存请求连接")


#保存数据
def write_csv(file_name, data_list):
    with open(file_name, mode='a') as csv_file:
        # headers = ['city', 'brand', 'series', 'model']
        writer = csv.writer(csv_file)
        for data in data_list:
            writer.writerow(data)
        # print("保存成功")


if __name__ == '__main__':
    city_ids = city_brand("all_city.json")
    brand_ids = city_brand("brand_id.json")
    brand_city_tuple = [(city_id, brand_id) for city_id in city_ids for brand_id in brand_ids][7:10] #后续需要修改索引
    # total_urls = [primary_url + brand_city_tuple[i][1] + brand_city_tuple[i][0] for i in brand_city_tuple]  # 构建所有的请求url
    page_list = [i for i in range(0,3)]  #后续需要修改页面数

    for i in range(len(brand_city_tuple)): #循环城市和品牌

        page = 0
        while page in page_list:
            url = make_url(brand_city_tuple[i][0],brand_city_tuple[i][1], page)
            print("本次查找的城市&品牌是：", brand_city_tuple[i], "目前的页数是：", page)
            #默认都从第0页开始抓取，抓取过程先判断是否有车辆信息，没有说明该城市+品牌组合没有数据，退出while循环，开始下一次for循环
            html, page_result = get_response(url)  #此处调用函数获取网页源码
            print("页面结果：-----", page_result)
            if "很抱歉暂时没有发现您要找的车，" in page_result:
                print("该城市&该品牌没有相关二手车")
                with open('zero_result_url.txt', mode='a') as f:
                    f.write(url)
                    f.write('\n')
                break
            else:
                title, info, source, price, gap_price = parse_html(html)  #调用函数解析页面源码
                # result = [title, info, source, price, gap_price]
                # headers = ['title', 'info', 'source', 'price', 'gap_price']
                # print(result)
                #得到初始字段后，调用函数进一步处理字段
                data_list = split_field(title, info, source, price, gap_price)
                print("保存前查看数据：", data_list)
            #保存数据
            write_csv("che300.csv", data_list)
            print("保存成功")
            page += 1
            with open('request_url.txt', mode='a') as f:
                f.write(url)
                f.write('\n')

















# for i in range
# //*[@id="img_2_1"]/p
# //*[@id="img_2_1"]/p
# /html/body/div[4]/div[1]/ul[1]/li[1]/div/a/p
# /html/body/div[4]/div[1]/ul[1]/li[2]/div/a/p
# /html/body/div[4]/div[1]/ul[5]/li[2]/div/a/p

#返回基础页代码后，解析页面
#xpath
#统计有多少个车系ID
# url_counts = 1
# detail_url = response.xpath("//a[@href=]")



# #请求链接
# base_url = "https://www.che300.com/buycar/b5v1c1?rt=1612348764127"
# #构造请求头
# headers = {
#     'authority':'www.che300.com',
#     'accept-language':'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6',
#     'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'accept-encoding':'gzip, deflate, br',
#     'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
#     'Cookie':'Hm_lpvt_f33b83d5b301d5a0c3e722bd9d89acc8=1612348748; _che300=7JjT0vp3niXTwBmaMEIKWov9uGhY79wGe3LMoA2et+NccrmKn9768G299dRWwynd71aoEjQwm1EXHZNjTUzHBOku5H5OvTGy5EEYeNjQdJPs2w4+BufaM07R4VT0yKEcS0+MTeqdEfklAT6DxZbtkOhyAZ9WSJ4bglMQi6DEacd85ESxSIyprev5EO/iqgmWq3CAI+OeNtVYMIIRdscz18ESp7M1a2suPlOBGaN9h2K7biX/X2ft7/2Pgt0WULkAWz8HfwcQpwNp4ZPn5LeLNv+CjTGMZu84fe3zOfmWBaA6g/fXKb9ccbV21mmca+DxdoWgRKcr005CJW7Hxjj4Xa0thswoR2gyUjrMZA5rLrwRWjOMJns6eTTAcnPgEQLqqmtpGd8o1DIXYLUdVGmTMIUu6ffjSs705Rzrg3AMX/3rumTAlgXW751A9dWzyFkiDJVSHmjNmwGNjrj5rg8cP/ILmQiHbUc2BBpZtP/eMwJ/G6tnbdDIM+KlBVmt0HCjpDb6OYmgKVUaiLcxGgHdbnRouwpvFofzf8i/qLRuIUIHgdWXzYaJUmizTmDBRqlQX7sRZBuxYpAAdye5pw5jyw==a6adf78b5666564f7ff4c2a922172aedfcf3db1e'
# }
#
# #发送请求
# r = requests.get(base_url,headers=headers)
#
# print(r.text)

#che300.demo
#整体思路&流程：先请求一个基础页面，以城市+品牌的方式，获取到第一页中的二手车标题和对应的跳转链接，然后再分别请求这几个链接，在每次请求
#中获取最终所需的字段值
#前提条件：知道内容对应的HTML标签位置
#基础页的二手车标题：<p class="list-title">2015款 宝马3系 320i 时尚型</p>
#基础页的二手车跳转链接：<a href="https://www.che300.com/buycar/x33891996" title="点击查看2015款>

#方案2：爬取完当前页面后，构造下一页的url
#思路：
# base_url = "http://www.che300.com/buycar/"
# page_index = html.xpath("/html/body/div[4]/div[2]/span/text()")
# #获取页面数
# page_length = 1
# page_id = [20*i for i in range(1,)]
# next_page_url = 1
#
# for page in range(10):
#     a = {page * 20}
#     print(a)
#     xpath = "//*[@id="scroll_post"]/div[1]/p[29]"

#二手车价格详情页
# """
# 报价：<div class="dtir-price clear-fix"> <strong>￥17.22万</strong>
# /html/body/div[2]/div/div[2]/div/div[2]/div[1]/strong
# 新车最低价：<span id="lowestNewPrice">30.77万</span>
# 股价：<p>"估价:17.12万"</p>
# 上牌日期：<span>2014年09月</span>
# 公里数：<span>4.2万公里</span>
# 所在地：<span>昆明</span>
# 排放标准：<span>国5</span>
#
# 亮点配置：<div>后驻车雷达</div>  <div>胎压监测</div>
#
# 基本信息
# 车身颜色：<li>车身颜色</li><li>红色</li>
# 变速箱：<li></li><li></li>
# 排量：<li></li>
# 下一年估值：<li></li>
#
# """
#
# # second_urls = []
#
# #
# for url in second_urls:
#     response = requests.get(url)

#     #解析页面获取所需字段
#     city =
#     brand =
#     model =
#     year_of_car =
#     miles =
#     box =
#     gas =
#     standard =
#     lowest_price =
#     round_price =
#     owner_price =
#     next_year_price =
#     device =
#     #用一个列表保存一个车系的所有字段：
#     series_list = []
#     return city, brand, model, year_of_car, miles, box, gas, \
#            standard, lowest_price, round_price, owner_price, next_year_price, device

#判断页面
# import re
# info_nocar = "暂时没有发现您要找的车"
# response_info = html.xpath("/html/body/div[3]/div/p/text()[1]")
# if response_info == "很抱歉暂时没有发现您要找的车， "：
#     continue
# else:
#     pass

# #保存爬取数据
#保存的问题
#1.保存到本地，CSV格式
# import csv
# headers = []
# info_car_list = [city, brand, series, model, price, source, gap_price, high_low]
# with open('car_info.csv','w') as f:
#     csv_write = csv.writer(f, dialect='excel')
#     csv.write.writerow(headers)