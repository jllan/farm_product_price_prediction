import re
import csv
import requests
import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup

PRODUCT_LIST = {
    '蔬菜': {
        'id': '13075',
        'name': {
            '西红柿': '20414',
            '土豆': '20413'
        }
    }
}

MARKET_LIST = {
    '江苏':  {
        'id': '32',
        'name':{
            '南京农副产品物流中心': '22346058'
        }
    }
}



class PriceSpider:
    def __init__(self, product, market, type_id='13075', province_id='32'):
        self.url = 'http://nc.mofcom.gov.cn/channel/gxdj/jghq/jg_list.shtml'
        client = MongoClient('localhost', 27017)
        db = client['product_prices']
        self.collection = db['prices']
        self.province_id = province_id
        self.type_id = type_id
        self.product_id = PRODUCT_LIST['蔬菜']['name'].get(product)
        self.market_id = MARKET_LIST['江苏']['name'].get(market)

    def get_data(self, start_date, end_date, page=1):
        print('日期{}, 页数{}'.format(start_date, page))
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID=013C8A82A78D0207E9972622358F3EBA; jiathis_rdc=%7B%22http%3A//nc.mofcom.gov.cn/articlexw/xw/dsxw/201701/19106095_1.html%22%3A%220%7C1483600753441%22%7D; Hm_lvt_166c4f5298175046e0af03a413b3784e=1483503291; Hm_lpvt_166c4f5298175046e0af03a413b3784e=1483603019',
            'Host': 'nc.mofcom.gov.cn',
            'Referer': 'http://nc.mofcom.gov.cn/channel/gxdj/jghq/jg_list.shtml?par_craft_index=13075&craft_index=20414&startTime=2014-01-01&endTime=2014-04-01&par_p_index=32&p_index=22346058&keyword=&page=1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        data = {
            'par_craft_index': self.type_id,
            'craft_index': self.product_id,
            'startTime': start_date,
            'endTime': end_date,
            'par_p_index': self.province_id,
            'p_index': self.market_id,
            # 'keyword:
            'page': page
        }
        try:
            res = requests.get(self.url, headers=headers, params=data)
            assert res.status_code == 200
            print(res.url)
            # print(res.text)
            return res.text
        except Exception as e:
            print('date {}, page {} error: {}'.format(start_date, page, e))
            return None

    def parse_data(self, data):
        soup = BeautifulSoup(data)
        prices = soup.find('div', {"class": "pmCon"}).select('tr')[1:]
        # print(prices)
        items = []
        for price in prices:
            item = {}
            p = price.select('td')
            item['title'] = p[0].text.strip()
            item['price'] = p[1].text.strip()
            item['market'] = p[2].text.strip()
            item['date'] = p[3].text.strip()
            print(item)
            items.append(item)
        return items

    def get_total_page(self, data):
        pattern = re.compile('var\s+v_PageCount\s+=\s+(\d+)')
        pages = re.findall(pattern, data)[0]
        return int(pages)

    def process_item(self, item):
        if not self.collection.find_one({
            'title': item['title'],
            'date': item['date']
        }):
            self.collection.insert(item)

    def run(self):
        start_date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d')
        interval = 90
        end_date = start_date
        while str(end_date)<'2017':
            end_date = start_date + datetime.timedelta(days=interval)
            page = pages = 1
            while page <= pages:
                data = self.get_data(str(start_date).split()[0], str(end_date).split()[0], page)
                items = self.parse_data(data)
                for item in items:
                    self.process_item(item)
                if page == 1:
                    pages = self.get_total_page(data)
                page += 1
                # next_page = self.have_next_page()
            start_date = end_date + datetime.timedelta(days=1)

if __name__ == '__main__':

    product = '西红柿'
    market = '南京农副产品交流中心'
    # type_id = product_list['蔬菜']['id']
    # product_id = product_list['蔬菜']['name'].get(product)
    # province_id = market_list['江苏']['id']
    # market_id = market_list['江苏']['name'].get(market)
    # print(type_id, product_id, province_id, market_id)
    print('开始采集{} {}的数据'.format(market, product))
    spider = PriceSpider(product, market)
    spider.run()