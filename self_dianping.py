# coding=utf-8
import requests
import re
import csv
from lxml import etree

font_size = 12

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


# 1.1 获得css样式的链接
def get_css_link(url):
    ''' 获取css链接 '''
    print('--->start-1.1-get_css_link--------------------------')
    # 获取网页源码
    html_origin = requests.get(url, headers=headers).text
    # 正则表达式匹配css链接
    css_link = re.search('<link rel="stylesheet" type="text/css" href="(//s3plus.meituan.net.*?.css)">', html_origin,
                         re.S)
    # print(css_link.group(1))
    css_link = 'http:' + css_link.group(1)
    html_css = requests.get(css_link, headers=headers).text

    print('==================================1.1>>>over!')

    return html_origin, html_css


# 1.2 获取前两个个字母
def get_front_two_alp(html_origin, class_name):
    '''获取地址的隐藏字体的class_name　前三个字母'''
    print('--->start-1.2-get_front_two_alp----------------')
    # 通过一级span的class_name,取出其子标签的class_name前三个字母

    front_three_alp = re.search('<span class="' + class_name + '">.*?<span class="(\w\w).*?"></span>', html_origin,
                                re.S)
    # print('打印地址的前两个字母')
    # print(front_alp_addr.group(1))
    print('==================================1.2>>>over!')
    # 返回地址的class_name的前三个字母

    return front_three_alp.group(1)


# 1.3 获取svg_link
def get_svg_link(html_css, front_two_alp_addr):
    # 获取的svg链接
    print('--->start-1.3-get_svg_link--------------------------')
    alp = front_two_alp_addr
    # print(alp)
    background_image_link = re.search(alp + '"]{.*?background-image: url\((//.*?svg)\)', html_css)
    # print(background_image_link.group(1))
    background_image_link = 'http:' + background_image_link.group(1)
    print('==================================1.3>>>over!')

    return background_image_link  # 地址对应此链接


# 2. 筛选有关地址的css,(background,x,y)
def get_font_css(html_css, front_alp_addr):
    '''获取html_css里面有关地址的(class_name,x,y)'''
    print('--->start-2-get_font_css--------------------------')

    font_css = re.findall('\.({0}\w\w\w)'.format(front_alp_addr) + '{background:-(\d+).0px -(\d+).0px;}', html_css,
                          re.S)
    # print('addr_css')
    # print(font_css)
    print('==================================2>>>over!')

    return font_css


######################################  3.为解密方法
# 3.1获得class_name 对应的文字  //第一种加密方法－old－有M0
def get_font_dict_by_offset_old(addr_svg_link, addr_css):
    '''获取坐标偏移的文字字典'''
    print('--->start-3.1-get_addr_font_dict_by_offset--------------')
    # print(addr_css)
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
        for addr_css_name_x_y in addr_css:
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
        print('==================================3.1>>>over!')

        return font_list


# 3.2获得class_name 对应的文字  //第二种加密方法－new－无M0
def get_font_dict_by_offset_new(svg_link_num, food_kind_css):
    '''获取坐标偏移的文字字典'''
    print('--->start-3.2-get_addr_addr_dict_by_offset_new--------------')
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
        print('==================================3.2>>>over!')

        return font_list


#########################################################################…………上
# 4. 获取地址
def get_result_font(html_origin, font_list, head_span_class_name):
    print('--->start-4-get_addr--------------------------')
    # print(font_list)
    for font in font_list:
        html_origin = html_origin.replace('<span class="' + font[0] + '"></span>', font[1])
    # 替换成功提取地址
    result_font = re.findall('<span class="' + head_span_class_name + '">(.*?)</span>', html_origin, re.S)
    # print(result_font)
    print('==================================4>>>over!')

    return result_font


# 5.获取店铺的菜种类
def get_food_kind(html_origin, html_css):
    '''获取菜种类,为便于和主程序统一，以下序号从1.2开始'''
    class_name = 'tag'  # 店铺菜种类的标签
    print('--->start-5-get_food_kind----------####################################')

    # 1.2 获取有关菜种类的前三个字母
    front_two_alp_food_kind = get_front_two_alp(html_origin, class_name='tag')
    # print('菜种类的前两个字母：' + front_two_alp_food_kind)

    # 1.3　获取菜种类对应的svg链接
    food_kind__svg_link = get_svg_link(html_css, front_two_alp_food_kind)
    # print('菜种类的链接：'+food_kind__svg_link)

    # 2. 获取html_css有关菜种类的（background,x,y)
    food_kind_css = get_font_css(html_css, front_two_alp_food_kind)
    # print('菜种类的css')
    # print(food_kind_css)

    # 3. 获取css样式对应的菜种类字典文件  //第一种加密方法－old－有M0
    font_list = get_font_dict_by_offset_old(food_kind__svg_link, food_kind_css)
    # print('class_name对应的文字')
    # print(font_list)

    # 4. 获取地址
    result_font = get_result_font(html_origin, font_list, head_span_class_name='tag')

    # 重新组成新的列表,将[0,1,2,3,5,6,7,8]=>[(0,1),(2,3),(5,6),(7,8)] . (菜种类，所在区)
    a = iter(result_font)
    b = zip(a, a)
    food_kind_and_area = []
    for i, j in b:
        food_kind_and_area.append((i, j))
    # print(food_kind_and_area)

    print('===#################################################=====5>>>over!')

    return food_kind_and_area


# 6.获取店铺的评论数和人均消费  # 标签样式和5不同，只能重写
def get_comment(html_origin, html_css, class_name_mean_price='mean-price'):
    # 6.1.2获取评论信息－－评论人数＆人均消费
    font_three_alp_num = get_front_two_alp_num(html_origin, class_name='review-num')

    # 6.1.3获取svg_link
    svg_link_num = get_svg_link_num(html_css, font_three_alp_num)

    # 6.2 筛选有关评论的css,(background,x,y)
    comment_css = get_comment_css(html_css, font_three_alp_num)

    # 6.3获得class_name 对应的数字
    font_list = get_num_font_dict_by_offset_new(svg_link_num, comment_css)
    # 获取口味环境服务数据
    comment_list_new = get_result_font_num(html_origin, font_list, head_span_class_name='comment-list')

    return comment_list_new


# 6.1.2 获取前三个字母
def get_front_two_alp_num(html_origin, class_name):
    '''获取地址的隐藏字体的class_name　前三个字母'''
    print('--->start-6.1.2-get_front_two_alp----------------')
    # 通过一级span的class_name,取出其子标签的class_name前三个字母
    front_three_alp = re.search('class="' + class_name + '.*?<span class="(\w\w).*?</span>', html_origin, re.S)
    # print('打印地址的前三个字母')
    # print(front_three_alp.group(1))
    print('==================================6.1.2>>>over!')
    # 返回地址的class_name的前三个字母

    return front_three_alp.group(1)


# 6.1.3 获取svg_link
def get_svg_link_num(html_css, front_three_alp):
    # 获取的svg链接
    print('--->start-6.1.3-get_svg_link_num--------------------------')
    alp = front_three_alp
    background_image_link = re.search(alp + '"].*?background-image: url\((//.*?svg)\)', html_css)

    background_image_link = 'http:' + background_image_link.group(1)

    # print(background_image_link)
    print('==================================6.3>>>over!')

    return background_image_link  # 地址对应此链接


# 6.2. 筛选有关评论的css,(background,x,y)
def get_comment_css(html_css, front_alp_addr):
    '''获取html_css里面有关地址的(class_name,x,y)'''
    print('--->start-6.2-get_comment_css--------------------------')

    comment_css = re.findall('\.({0}\w\w\w)'.format(front_alp_addr) + '{background:-(\d+).0px -(\d+).0px;}', html_css,
                             re.S)
    # print('comment_css')
    # print(comment_css)
    print('==================================6.2>>>over!')

    return comment_css


# 6.3.2获得class_name 对应的文字
def get_num_font_dict_by_offset_new(svg_link_num, comment_css):
    '''获取坐标偏移的文字字典'''
    print('--->start-6.3.2-get_num_font_dict_by_offset_new--------------')
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
        # print('font_finded')
        # print(font_finded)
        offset_x = []
        offset_y = []
        font_list = []
        for comment_css_name_x_y in comment_css:
            for y in y_list:
                if int(comment_css_name_x_y[2]) < int(y):

                    offset_x = int((int(comment_css_name_x_y[1]) / 12))
                    # print('offset_x')
                    # print(offset_x)
                    for one_y in y_list_new:
                        if int(one_y[1]) == int(y):
                            offset_y = one_y[0]
                            # print('offset_y')
                            # print(offset_y)
                            font_list.append((comment_css_name_x_y[0], font_finded[offset_y][offset_x]))

                    break

        # print(font_list)
        print('==================================6.3.2>>>over!')

        return font_list


# 6.4. 获取口味环境服务数据
def get_result_font_num(html_origin, font_list, head_span_class_name):
    print('--->start-6.4-get_addr--------------------------')
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

    print('==================================6.4>>>over!')

    return comment_list_new

# 7. 获取店铺有名称
def get_shop_name(html_origin):
    print('--->start-7--get_shop_name--------------------------')
    # print(html_origin)
    shop_name = re.findall('class="txt">.*?<h4>(.*?)</h4>',html_origin,re.S)

    # print(shop_name)
    print('==================================7>>>over!')

    return shop_name

def main():
    ############################-------获取地址-----------#########################################
    url = 'http://www.dianping.com/beijing/ch10/g311'
    # 1.1 获取css样式文件
    html_origin, html_css = get_css_link(url)

    # 1.2　获取地址的前两个字母 地址的class=addr,传入addr
    front_two_alp_addr = get_front_two_alp(html_origin, class_name='addr')

    # 1.3 获取地址对应的svg链接
    addr_svg_link = get_svg_link(html_css, front_two_alp_addr)

    # 2. 获取html_css有关地址的（background,x,y)
    font_css = get_font_css(html_css, front_two_alp_addr)

    # 3.2 获取css样式对应的地址字典文件  //第二种加密方法－new－无M0
    font_list = get_font_dict_by_offset_new(addr_svg_link, font_css)

    # 4. 获取地址　　/** 这里有一个地址字典后续要用
    addr_font = get_result_font(html_origin, font_list, head_span_class_name='addr')

    #################################################################################################
    # 5.获取店铺的菜种类 /** 这里有一个菜种类和区域字典后续要用
    food_kind_and_area = get_food_kind(html_origin, html_css)
    ################################################################################################
    # 6.获取店铺的口味环境服务水平 /** 这里有一个口味环境服务水平后续要用
    comment_list_new = get_comment(html_origin, html_css)

    # 7.获取店铺名称
    shop_name = get_shop_name(html_origin)

    # 8. 制成csv格式
    zipped = zip(shop_name,food_kind_and_area,comment_list_new)
    with open('table.csv','w') as f:
        writer = csv.writer(f)
        writer.writerow(['店名','种类和区域','评价'])
        for i in zipped:
            writer.writerow(i)

        # print(i)


if __name__ == '__main__':
    main()
