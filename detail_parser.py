from lxml import etree
import requests
from config import *
import time
import datetime
import re


class ParseUrlDetail:

    def __init__(self, url):
        # 目标爬取url配置
        self.url = url
        # 反爬配置
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
        self.cookies = {'Cookie': COOKIE}
        self.headers.update(self.cookies)
        # print(self.headers)

    @staticmethod
    def check_item(item, *args):
        """
        用于替代try - except 形成的重复代码；
        判断列表是否存在元素，如果不存在则赋予一个空字符串列表用于
        :param item: xpath 所获取的列表信息
        :param args: 传入值应该为列表
        :return:
        """
        if len(item) == 0:
            item = ['', 'this item is None']
        return item

    @staticmethod
    def duplicated_list(item, *args):
        """
        实现列表的去重功能，同时删除列表中的空字符串
        :param item: 列表
        :param args: 传入值为列表
        :return: 去重后的 且没有空字符串的列表
        """
        new_list = []
        for i in set(item):
            if i.strip() != '':
                new_list.append(i.strip())
        return new_list

    # 下载页面html
    def download_response(self):
        response = requests.get(url=self.url, headers=self.headers)
        if response.status_code == 200:
            return response.text

    # 页面解析
    def parse_response_text(self, response_text):
        print(response_text)
        html = etree.HTML(response_text)
        # 图片链接
        pic_50_list = html.xpath('//div[@id="altImages"]//li[contains(@class,"a-spacing-small item")]//img/@src')
        print(pic_50_list)
        pic_id = pic_50_list[0].split('/')[5].split('.')[0]
        # 品牌名称
        brand = html.xpath('//a[@id="bylineInfo"]/text()')
        # 商品名称
        title = html.xpath('string(//h1[@id="title"])').strip()
        # 同系列的商品asin列表
        series_asin_list = html.xpath('//ul[@role="radiogroup"]/li/@data-defaultasin')
        for dp_url in html.xpath('//ul[@role="radiogroup"]/li/@data-dp-url'):
            if dp_url and '/' in dp_url:
                series_asin_list.append(dp_url.split('/')[2])

        series_asin_list = ParseUrlDetail.duplicated_list(series_asin_list)
        # 获取评分
        score = html.xpath('//span[@id="acrPopover"]/@title')[0].replace(' out of 5 stars', '')
        # 获取 评论人数
        comment_num = html.xpath('string(//span[@id="acrCustomerReviewText"])').replace('ratings', '').replace(',', '').strip()
        # 获取 被回答问题数
        answered_questions_num = html.xpath('string(//a[@id="askATFLink"]/span)').replace('answered questions', '').strip()
        # 价格信息
        list_price = ParseUrlDetail.check_item(html.xpath('//div[@id="price"]//td[contains(text(),"List")]/../td[2]/span/text()'))[0]
        # list_price = html.xpath('//span[@id="listPriceLegalMessage"]/../span/text()')
        priceblock_ourprice = html.xpath('//div[@id="price"]//span[@id="priceblock_ourprice"]/text()')[0]
        # 是否包邮
        is_free_shipping = 'free shipping' in html.xpath('string(//div[@id="price"])').lower()
        # 是否能够免费退货
        is_free_return = 'free return' in html.xpath('string(//div[@id="price"])').lower()

        # 可售店铺数
        sale_stores_num = html.xpath('//div[contains(@id, "olp") and contains(@id, "new")]//a/text()')
        # 货比三家url
        # compare_price_url = 'https://www.amazon.com/gp/offer-listing/{}/ref=dp_olp_new?ie=UTF8&condition=new'.format(asin)

        # 可以从这些卖家购买的跳转链接
        try:
            buy_from_url = 'https://www.amazon.com' + \
                           html.xpath('//div[@id="availability"]//a[contains(@href, offer)]/@href')[0]
        except:
            buy_from_url = ''
        # 可选商品类型
        item_type = html.xpath('string(//form[@id="twister"])')
        # 标题下面的描述
        under_title_desc = html.xpath('string(//ul[@class="a-unordered-list a-vertical a-spacing-none"])')

        # 使用场景和材质信息等
        # 对列表进行初始化操作
        # 判断是否具有中间介绍的表格
        init_value_list = []
        apm_table = html.xpath('//table[@class="apm-tablemodule-table"]/tbody')
        if len(apm_table) > 0:
            apm_table = apm_table[0]
            item_type_num = len(apm_table.xpath('./tr[1]/th')) - 1
            # 判断是否具有多个可选item
            if item_type_num > 0:

                # 对于每行数据进行迭代 输出 [{key:value_list}, ...]
                for tr in apm_table.xpath('./tr'):
                    # 由于前两行没有th标签，所以对前两行提取
                    if 'apm-tablemodule-imagerows' in ','.join(tr.xpath('./@class')):
                        # 判断是否为图片行
                        if 'apm-tablemodule-image' in ','.join(tr.xpath('./th/@class')):
                            img_url_list = tr.xpath('./th[contains(@class,"apm-tablemodule-image")]//img/@src')
                            href_list = tr.xpath('./th[contains(@class,"apm-tablemodule-image")]/a/@href')
                            init_value_list.append({'img_url_list': img_url_list, 'href_list': href_list})
                        # 判断是否为图片描述行
                        else:
                            item_env_list = tr.xpath('./th/a/text()')
                            init_value_list.append({'item_env_list': [env.strip() for env in item_env_list]})
                    # 对之后的材质等因素行进行输出
                    elif 'apm-tablemodule-keyvalue' in ','.join(tr.xpath('./@class')):
                        key = tr.xpath('string(./th)').strip()
                        value_list = tr.xpath('./td//span/text()')
                        init_value_list.append({key: [value.strip() for value in value_list]})


        # Tech information
        weight = ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Weight")]/../td/text()'))[0].strip()
        dimensions = ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Dimensions")]/../td/text()'))[
            0].strip()
        model_num = ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"model number")]/../td/text()'))[
            0].strip()
        color = ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Color")]/../td/text()'))[0].strip()
        items_num = ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Number of Items")]/../td/text()'))[
            0].strip()
        size = ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Size")]/../td/text()'))[0].strip()
        manufacturer_part_number = \
            ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Manufacturer Part Number")]/../td/text()'))[
                0].strip()

        # Additional information
        # 热销商品排名
        try:
            best_sellers_rank = html.xpath('string(//tr//th[contains(text(),"Best Sellers Rank")]/../td)').strip()
        except:
            best_sellers_rank = html.xpath('string(//li[@id="SalesRank"])')

        # 发货重量
        shipping_weight = \
            ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Shipping Weight")]/../td/text()'))[
                0].strip()
        # 上架时间
        date_first_available = \
            ParseUrlDetail.check_item(html.xpath('//tr/th[contains(text(),"Date First Available")]/../td/text()'))[
                0].strip()

        return {
            'pic_50_list': pic_50_list,
            'main_pic': pic_50_list[0],
            'asin': self.url.replace('https://www.amazon.com/dp/product/', ''),
            'pic_id': pic_id,
            'title': title,
            'series_asin_list': series_asin_list,
            'score': score,
            'comment_num': comment_num,
            'answered_questions_num': answered_questions_num,
            'list_price': list_price,
            'priceblock_ourprice': priceblock_ourprice,
            'is_free_shipping': str(is_free_shipping),
            'is_free_return': str(is_free_return),
            'brand': brand[0],
            'weight': weight,
            'dimensions': dimensions,
            'model_num': model_num,
            'color': color,
            'items_num': items_num,
            'size': size,
            'manufacturer_part_number': manufacturer_part_number,

            'useful_info': init_value_list,

            'best_sellers_rank': best_sellers_rank,
            # 'best_sellers_rank_html': best_sellers_rank_html,
            'shipping_weight': shipping_weight,
            'date_first_available': date_first_available,
            'date': datetime.date.today().strftime('%Y%m%d')
        }


if __name__ == '__main__':
    url_list = ['https://www.amazon.com/dp/product/B083JCXPY1/',  # 用于检测基本字段能否抓取
                'https://www.amazon.com/dp/product/B01KB9WM2S/',  # 用于检测不同的图片展现方式能否抓取
                'https://www.amazon.com/dp/product/B07Y1X24KP']   # 用于检测不同系列的产品asin 能否抓取
    for url in url_list:
        parse_url_detail = ParseUrlDetail(url)
        response_text = parse_url_detail.download_response()
        # print(response_text)
        if response_text:
            json_data = parse_url_detail.parse_response_text(response_text)
            print(json_data)