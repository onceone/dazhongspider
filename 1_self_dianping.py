# coding=utf-8
import requests
import re
import csv
import time
from lxml import etree
from geopy.geocoders import Nominatim

font_size = 12

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


# 1.1 获得css样式的链接
def get_html_origin_css_link(url):
    ''' 获取网页源码和加密的css样式 '''

    # 获取网页源码
    html_origin = requests.get(url, headers=headers).text

    # 正则表达式匹配css链接
    css_link = re.findall('<link rel="stylesheet" type="text/css" href="(//s3plus.*?)">', html_origin, re.S)
    # print(css_link[0])
    css_link = 'http:' + css_link[0]
    # print(css_link)
    html_css = requests.get(css_link, headers=headers).text

    return html_origin, html_css


# ------------- down两种方法-------------------------
# 1.2.1 获取前两个字母
def get_front_two_alp(html_origin, class_name):
    '''获取地址的隐藏字体的class_name　前两个字母'''

    # 通过一级span的class_name,取出其子标签的class_name前两个字母

    front_two_alp = re.search('<span class="' + class_name + '">.*?<span class="(\w\w).*?"></span>', html_origin,
                              re.S)
    # print('打印地址的前两个字母')
    # print(front_two_alp.group(1))
    # 返回地址的class_name的前两个字母

    return front_two_alp.group(1)


# 1.2.2 获取前三个字母
def get_front_three_alp(html_origin, class_name):
    '''获取地址的隐藏字体的class_name　前三个字母'''

    # 通过一级span的class_name,取出其子标签的class_name前三个字母

    front_three_alp = re.search('<span class="' + class_name + '">.*?<span class="(\w\w\w).*?"></span>', html_origin,
                                re.S)
    # print('打印地址的前三个字母')
    # print(front_three_alp.group(1))
    # 返回地址的class_name的前三个字母

    return front_three_alp.group(1)


# -------------- up--------------------------------

# 1.3 获取svg_link
def get_svg_link(html_css, front_two_alp_addr):
    # 获取的svg链接
    alp = front_two_alp_addr
    print(alp)
    background_image_link = re.findall(alp + '"]{.*?background-image: url\((//.*?svg)\)', html_css)
    print(background_image_link[0])
    background_image_link = 'http:' + background_image_link[0]
    print(background_image_link)

    return background_image_link  # 地址对应此链接


# 2. 筛选有关地址的css,(background,x,y)
def get_font_css(html_css, front_alp_addr):
    '''获取html_css里面有关地址的(class_name,x,y)'''

    font_css = re.findall('\.({0}\w\w\w)'.format(front_alp_addr) + '{background:-(\d+).0px -(\d+).0px;}', html_css,
                          re.S)
    # print(font_css)

    return font_css


# -----------down 3.为两种解密方法--------------------
# 3.1获得class_name 对应的文字  //第一种加密方法－old－有M0
def get_font_dict_by_offset_old(addr_svg_link, font_css):
    '''获取坐标偏移的文字字典'''
    # print(font_css)
    svg_html = requests.get(addr_svg_link, headers=headers).text
    # print(svg_html)
    font_finded = {}

    y_list_M0 = re.findall('d="M0 (\d+)', svg_html)

    if y_list_M0:
        font_finded = re.findall('<textPath.*?>(.*?)<', svg_html)
        # print(font_dict)
        offset_x = []
        offset_y = []
        font_list = []
        for addr_css_name_x_y in font_css:
            for y in y_list_M0:
                if int(addr_css_name_x_y[2]) < int(y):
                    # print(str(addr_css_y[2]) + '--------' + str(y))
                    # print(y)
                    id_href_y = re.findall('<path id="(\d+)" d="M0 {} .*?/>'.format(y), svg_html)
                    # print('id_href_y')
                    # print(id_href_y)
                    offset_x = int((int(addr_css_name_x_y[1]) / 12))
                    # for y in id_href_y:
                    offset_y = int(id_href_y[0]) - 1
                    # print(addr_css_name_x_y[0])
                    font_list.append((addr_css_name_x_y[0], font_finded[offset_y][offset_x]))

                    break

        # print(font_list)

        return font_list


# 3.2获得class_name 对应的文字  //第二种加密方法－new－无M0
def get_font_dict_by_offset_new(svg_link_num, food_kind_css):
    '''获取坐标偏移的文字字典'''
    # print(addr_css)
    svg_html = requests.get(svg_link_num, headers=headers).text
    # print(svg_html)
    font_finded = {}

    y_list = re.findall('<text x=.*?y="(\d+)"', svg_html)
    # print('y_list:')
    # print(y_list)
    y_list_new = []
    for i in enumerate(y_list):
        y_list_new.append(i)
    # print('y_list_new')
    # print(y_list_new)
    # print(comment_css)
    if y_list:
        font_finded = re.findall('<text .*?>(.*?)<', svg_html)
        # print(font_finded)
        offset_x = []
        offset_y = []
        font_list = []
        for food_css_name_x_y in food_kind_css:
            for y in y_list:
                if int(food_css_name_x_y[2]) < int(y):

                    offset_x = int((int(food_css_name_x_y[1]) / 12))
                    # print('offset_x')
                    # print(offset_x)
                    for one_y in y_list_new:
                        if int(one_y[1]) == int(y):
                            offset_y = one_y[0]
                            font_list.append((food_css_name_x_y[0], font_finded[offset_y][offset_x]))

                    break

        # print(font_list)

        return font_list


# --------------up------------------------------------------------

# 4. 获取加密结果
def get_result_font(html_origin, font_list, head_span_class_name):
    # print(font_list)
    # font_list = iter(font_list)
    for font in font_list:
        html_origin = html_origin.replace('<span class="' + font[0] + '"></span>', font[1])
    # 替换成功提取加密文字
    result_font = re.findall('<span class="' + head_span_class_name + '">(.*?)</span>', html_origin, re.S)
    # print(result_font)

    return result_font


# ------------------------------------------------------------------------
# 5.获取店铺的美食类别和店铺所在区域
def get_food_kind_area(html_origin, html_css):
    '''获取美食类别和店铺所在区域,为便于和主程序统一，以下序号从1.2开始'''
    # class_name = 'tag'  # 店铺美食类别的标签

    # 1.2 获取有关美食类别和店铺所在区域的前三个字母
    front_two_alp_food_kind = get_front_three_alp(html_origin, class_name='tag')
    # print('美食类别的前两个字母：' + front_two_alp_food_kind)

    # 1.3　获取美食类别和店铺所在区域对应的svg链接
    food_kind__svg_link = get_svg_link(html_css, front_two_alp_food_kind)
    # print('美食类别的链接：'+food_kind__svg_link)

    # 2. 获取html_css有关美食类别和店铺所在区域（background,x,y)
    food_kind_css = get_font_css(html_css, front_two_alp_food_kind)
    # print('美食类别的css')
    # print(food_kind_css)

    # 3. 获取css样式对应的美食类别和店铺所在区域的字典文件  //第一种加密方法－old－有M0
    font_list = get_font_dict_by_offset_new(food_kind__svg_link, food_kind_css)
    # print('class_name对应的文字')
    # print(font_list)

    # 4. 获取美食类别和店铺所在区域的加密文字
    result_font = get_result_font(html_origin, font_list, head_span_class_name='tag')

    # 重新组成新的列表,将[0,1,2,3,5,6,7,8]=>[(0,1),(2,3),(5,6),(7,8)] . (美食类别，店铺所在区域)
    a = iter(result_font)
    b = zip(a, a)
    food_kind_and_area = []
    for i, j in b:
        food_kind_and_area.append((i, j))
    # print(food_kind_and_area)

    # 拆包　拆成(美食类别),(所在区)
    food_kind = []
    food_area = []
    for m in food_kind_and_area:
        food_kind.append(m[0])
        food_area.append(m[1])
    # print(food_kind)
    # print(food_area)

    return food_kind, food_area


# 6.获取店铺的评价，口味、环境、服务
def get_comment(html_origin, html_css):
    '''获取美食评价,(口味、环境、服务)为便于和主程序统一，以下序号从1.2开始'''
    class_name = 'tag'  # 店铺美食类别的标签

    # 1.2 获取有关美食评价,(口味、环境、服务)前三个字母
    front_two_alp_food_comment = get_front_three_alp(html_origin, class_name='comment-list')
    # print('美食评价,(口味、环境、服务)前两个字母：' + front_two_alp_food_comment)

    # 1.3　获取美食类别和店铺所在区域对应的svg链接
    food_kind__svg_link = get_svg_link(html_css, front_two_alp_food_comment)
    # print('美食评价的链接：'+food_kind__svg_link)

    # 2. 获取html_css有关美食类别和店铺所在区域（background,x,y)
    food_comment_css = get_font_css(html_css, front_two_alp_food_comment)
    # print('美食评价的css')
    # print(food_comment_css)

    # 3. 获取css样式对应的美食评价的字典文件  //第一种加密方法－new－无M0
    font_list = get_font_dict_by_offset_new(food_kind__svg_link, food_comment_css)
    # print('class_name对应的文字')
    # print(font_list)

    # 4. 获取美食评价的加密文字
    food_coment = get_food_comment_list(html_origin, font_list, head_span_class_name='comment-list')

    # print(food_coment)

    return food_coment


# 6.4. 获取口味环境服务数据
def get_food_comment_list(html_origin, font_list, head_span_class_name):
    # print('font_list')
    # print(font_list)
    for font in font_list:
        html_origin = html_origin.replace('<span class="' + font[0] + '"></span>', font[1])
    # 替换成功提取地址
    html_origin = re.sub('<b>|</b>|<span >|</span>', '', html_origin)

    # print(html_origin)
    result_font = re.findall('<span class="' + head_span_class_name + '">(.*?)</div>', html_origin, re.S)

    comment_list = []

    pattern = re.compile('\n      ')
    for result in result_font:
        result_font = re.sub(pattern, '', result)
        comment_list.append(result_font)

    comment_list_new = []
    for comment in comment_list:
        comment_list_new.append(comment.strip())

    # print('comment_list_new')
    # print(comment_list_new)

    return comment_list_new


# ----------down---review-num---------------------------------------
# 7.获取店铺的评价人数
def get_review_num(html_origin, html_css):
    font_two_alp = get_front_three_alp_num(html_origin, class_name='review-num')

    # 6.1.3获取svg_link
    svg_link_num = get_svg_link(html_css, font_two_alp)

    # 6.2 筛选有关评论的css,(background,x,y)
    comment_css = get_font_css(html_css, font_two_alp)

    # 6.3获得class_name 对应的数字
    font_list = get_font_dict_by_offset_new(svg_link_num, comment_css)

    # 获得评价人数
    comment_list_new = get_result_review_num_font(html_origin, font_list, head_span_class_name='review-num')

    return comment_list_new


# 解密，获得评价人数
def get_result_review_num_font(html_origin, font_list, head_span_class_name):
    # print(font_list)
    # font_list = iter(font_list)
    for font in font_list:
        html_origin = html_origin.replace('<span class="' + font[0] + '"></span>', font[1])
    # 替换掉<b>|</b>
    html_origin = re.sub('<b>|</b>', '', html_origin)

    # 替换成功提取加密文字
    result_font = re.findall('<a .*? class="' + head_span_class_name + '".*?>(.*?)</a>', html_origin, re.S)
    review_num = []
    pattern = re.compile('\n              ')
    for result in result_font:
        result_font = re.sub(pattern, '', result)
        review_num.append(result_font)

    pattern2 = re.compile('\n')
    r = []
    for i in review_num:
        j = re.sub(pattern2, ' ', i)
        r.append(j)
    # print(r)

    return r


# -----------up------------------------------------------------------------

# ----------------down-评价人数-前面字母(两种方法)-------------------------
# 1.2.1 获取评价人数前两个字母
def get_front_two_alp_num(html_origin, class_name):
    '''获取地址的隐藏字体的class_name　前两个字母'''
    # 通过一级span的class_name,取出其子标签的class_name前两个字母

    front_two_alp = re.search('<a .*? class="' + class_name + '".*?<span class="(\w\w).*?</span>', html_origin,
                              re.S)
    print('打印评价人数的前两个字母')
    print(front_two_alp.group(1))
    # 返回地址的class_name的前两个字母

    return front_two_alp.group(1)


# 1.2.1 获取评价人数和人均消费前三个字母
def get_front_three_alp_num(html_origin, class_name):
    '''获取地址的隐藏字体的class_name　前三个字母'''
    # 通过一级span的class_name,取出其子标签的class_name前三个字母

    front_two_alp = re.search('<a .*? class="' + class_name + '".*?<span class="(\w\w\w).*?</span>', html_origin,
                              re.S)
    print('打印评价人数的前三个字母')
    print(front_two_alp.group(1))
    # 返回地址的class_name的前两个字母

    return front_two_alp.group(1)


# ---------------------up-----------------------------------------------

# 8. 获取店铺有名称
def get_shop_name(html_origin):
    # print(html_origin)
    shop_name = re.findall('class="txt">.*?<h4>(.*?)</h4>', html_origin, re.S)

    # print(shop_name)

    return shop_name


# 9.获取店铺的详细地址
def get_addrs(html_origin, html_css):
    # 1.2　获取地址的前两个字母 地址的class=addr,传入addr
    front_two_alp_addr = get_front_three_alp(html_origin, class_name='addr')

    # 1.3 获取地址对应的svg链接
    addr_svg_link = get_svg_link(html_css, front_two_alp_addr)

    # 2. 获取html_css有关地址的（background,x,y)
    font_css = get_font_css(html_css, front_two_alp_addr)

    # 3.2 获取css样式对应的地址字典文件  //第二种加密方法－new－无M0
    font_list = get_font_dict_by_offset_new(addr_svg_link, font_css)

    # 4. 获取地址　　/** 这里有一个地址字典后续要用
    addr_font = get_result_font(html_origin, font_list, head_span_class_name='addr')

    # print(addr_font)
    return addr_font


# 获取地点经纬度
def get_lat_lng(addrs):
    lat = []  # 纬度
    lng = []  # 经度
    for addr in addrs:
        la, ln = geocodeB(addr)
        lat.append(la)
        lng.append(ln)
    # print(lat)
    # print(lng)

    return lat, lng


# 使用百度API
def geocodeB(address):
    base = url = "http://api.map.baidu.com/geocoder?address=" + address + "&output=json&key=XgNIhoyUC0VAytPu5q9suLLLM6yELqsG"
    response = requests.get(base)
    answer = response.json()
    return answer['result']['location']['lat'], answer['result']['location']['lng']


# 获得人均消费-----down-------------------------------------------------------------
def get_mean_price(html_origin, html_css):
    '''获得人均消费金额'''
    font_two_alp = get_front_three_alp_num(html_origin, class_name='mean-price')

    # 6.1.3获取svg_link
    svg_link_num = get_svg_link(html_css, font_two_alp)

    # 6.2 筛选有关评论的css,(background,x,y)
    comment_css = get_font_css(html_css, font_two_alp)

    # 6.3获得class_name 对应的数字
    font_list = get_font_dict_by_offset_new(svg_link_num, comment_css)

    # 获得评价人数
    mean_price = get_result_mean_price_font(html_origin, font_list, head_span_class_name='mean-price')
    # print(mean_price)

    return mean_price


# 解密　获得人均消费
def get_result_mean_price_font(html_origin, font_list, head_span_class_name):
    # print(font_list)
    # font_list = iter(font_list)
    for font in font_list:
        html_origin = html_origin.replace('<span class="' + font[0] + '"></span>', font[1])
    # 替换掉<b>|</b>
    html_origin = re.sub('<b>|</b>|</span>|￥', '', html_origin)
    # print('html_origin')
    # print(html_origin)
    # 替换成功提取加密文字
    result_font = re.findall('<a .*? class="' + head_span_class_name + '".*?>(.*?)</a>', html_origin, re.S)
    # print('result_font')
    # print(result_font)

    # 删除不必要的字符
    m = []  # 暂时代替mean_price
    pattern = re.compile('\n            |\n        |')
    print('-' * 100)
    for result in result_font:
        result_font = re.sub(pattern, '', result)
        m.append(result_font)
    # print(m)

    mean_price = []
    for i in m:
        mean_price.append(i[2:])  # 删除“人均”

    # print(mean_price)

    return mean_price


# ---------------up------------------------------------------------------------------

def main():
    shop_name_l = []  # 店铺名称
    addr_l = []  # 店铺详细地址
    lat_l = []  # 店铺所处纬度
    lng_l = []  # 店铺所处经度
    food_kind_l = []  # 美食类别
    food_area_l = []  # 店铺所在区域
    comment_list_l = []  # 口味环境服务评价
    review_num_l = []  # 评价人数
    mean_price_l = []  # 平均消费

    num = 0
    while num < 1:
        url = 'http://www.dianping.com/beijing/ch10/g311p{}'.format(num)

        # 1.1 获取网页源码和css样式
        html_origin, html_css = get_html_origin_css_link(url)

        # 8. 获取店铺的详细地址
        print('get_addrs--------------------------------------------------------------------------------------start')
        addrs = get_addrs(html_origin, html_css)
        print('get_addrs--------------------------------------------------------------------------------------over')

        # 5.获取店铺的美食类别和店铺所在区域 /** 这里有一个美食类别和区域字典后续要用
        print('get_food_kind_area-----------------------------------------------------------------------------start')
        food_kind, food_area = get_food_kind_area(html_origin, html_css)
        print('get_food_kind_area-----------------------------------------------------------------------------over')

        # 6.获取店铺的口味环境服务水平 /** 这里有一个口味环境服务水平后续要用
        print('get_comment_list-------------------------------------------------------------------------------start')
        comment_list = get_comment(html_origin, html_css)
        print('get_comment_list-------------------------------------------------------------------------------over')

        # 7.获得评价人数
        print('get_review_num----------------------------------------------------------------------------------start')
        review_num = get_review_num(html_origin, html_css)
        print('get_review_num----------------------------------------------------------------------------------over')

        # 8.获取店铺名称
        print('get_shop_name------------------------------------------------------------------------------------start')
        shop_name = get_shop_name(html_origin)
        print('get_shop_name------------------------------------------------------------------------------------over')

        # 9. 获取店铺地址的经纬度
        print('get_lat_lng---------------------------------------------------------------------------------------start')
        lat, lng = get_lat_lng(addrs)
        print('get_lat_lng---------------------------------------------------------------------------------------over')

        # 10.获得人均消费
        print('get_mean_price-----------------------------------------------------------------------------------start')
        mean_price = get_mean_price(html_origin, html_css)
        print('get_mean_price-----------------------------------------------------------------------------------over')

        # 一个循环惊醒追加各列表
        shop_name_l.append(shop_name)  # 店铺名称
        food_kind_l.append(food_kind)  # 美食类别
        food_area_l.append(food_area)  # 店铺所在区
        addr_l.append(addrs)  # 店铺详细地址
        lat_l.append(lat)  # 店铺所在纬度
        lng_l.append(lng)  # 店铺所在经度
        mean_price_l.append(mean_price)  # 平均消费
        review_num_l.append(review_num)  # 评价人数
        comment_list_l.append(comment_list)  # 评价值(口味服务环境）

        num += 1
        print('--------第{}个回合--------------------------------------'.format(num))
        time.sleep(1)


    # 8. 制成csv格式
    # 先拆包
    shop_name = shop_name_l[0]
    food_kind = food_kind_l[0]
    food_area = food_area_l[0]
    addr = addr_l[0]
    lat = lat_l[0]
    lng = lng_l[0]
    mean_price = mean_price_l[0]
    review_num = review_num_l[0]
    comment_list = comment_list_l[0]


    zipped = zip(shop_name, food_kind, food_area, addr, lat, lng, mean_price, review_num,comment_list)
    with open('table.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['店名', '美食类别', '区', '详细地址', '纬度', '经度', '平均消费', '评价人数', '评价值'])
        for i in zipped:
            writer.writerow(i)

            # print(i)


if __name__ == '__main__':
    main()
