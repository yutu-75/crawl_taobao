import json
import re
import time
import hashlib
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class CrawlTaoBao:
    def __init__(self):
        self.t = int(time.time() * 1000)
        self.app_key = "12574478"
        self.headers = {
            'authority': 'h5api.m.taobao.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': 'https://www.taobao.com/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': UserAgent().random        # 随机生成一个User-Agent
        }

        # Todo ["cna","sgcookie"] 生成方法没写, 待写...
        self.cookies = {
            'cna': 'fHKVHZ23KEMCARsLEYfFlegU',
            'sgcookie': 'E100fRiNqBPwDU36l9G1AiXsLbBcnOLqqJ1Xu%2BgWIgP2r%2B1s6bw8jOLpFJEmWTcWhCFSLVHJeetttNAZdmAQRDy4AEOzBLFohJpDVTHik4ifkJICcS7JFQ5AqZUQp1gyC%2Fmc',
            # 'isg': 'BB0dLh-OJPY-dsDauvWnwbDTLPkXOlGM_8mxTN_iXnSjlj3Ip4sZXOGAwIqQDmlE',
        }
        self.update_cookies()

    def get_sign(self, data):
        """
        获取 sign
        Args:
            data:

        Returns:

        """

        datas = f'{self.cookies["_m_h5_tk"].split("_")[0]}&{str(self.t)}&{self.app_key}&{data}'
        sign = hashlib.md5()  # 创建md5对象
        sign.update(datas.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
        signs = sign.hexdigest()  # 加密
        return signs

    def update_cookies(self) -> None:
        """
        获取访问接口的token
        Returns:

        """
        self.t = int(time.time() * 1000)
        params = {
            'jsv': '2.5.1',
            'appKey': self.app_key,
            't': self.t,
            'api': 'mtop.taobao.wireless.home.awesome.pc.get',
            'v': '1.0',
            'type': 'jsonp',
            'dataType': 'jsonp',
            'timeout': '3000',
            'callback': 'mtopjsonp4',
        }

        response = requests.get(
            'https://h5api.m.taobao.com/h5/mtop.taobao.wireless.home.awesome.pc.get/1.0/',
            params=params,
            headers=self.headers,
        )
        self.cookies["_m_h5_tk"] = response.cookies.get("_m_h5_tk")
        self.cookies["_m_h5_tk_enc"] = response.cookies.get("_m_h5_tk_enc")

    def search_commodity(self, name="女装", page_count=1, page_size=60):
        """
        Args:
            name:

        Returns:
        :param name:
        :param page_count:
        :param page_size:

        """

        data = str({
            "pNum": page_count,
            "pSize": f"{page_size}",
            "refpid": "mm_26632258_3504122_32538762",
            "variableMap": str({"q": f"{name}"}),
            "qieId": "36308"
        })

        params = {
            'jsv': '2.5.1',
            'appKey': self.app_key,
            't': self.t,
            'sign': self.get_sign(data),
            'api': 'mtop.alimama.union.xt.en.api.entry',
            'v': '1.0',
            'AntiCreep': 'true',
            'timeout': '20000',
            'AntiFlood': 'true',
            'type': 'jsonp',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp3',
            'data': data
        }

        response = requests.get(
            'https://h5api.m.taobao.com/h5/mtop.alimama.union.xt.en.api.entry/1.0/',
            params=params,
            cookies=self.cookies,
            headers=self.headers,
        )

        data = self.parse_json_from_string(response.text)['data']["recommend"]["resultList"]
        commodity_information_list = []
        for item in data:
            dict1 = {
                "item_name": item['itemName'],                                      # 衣服名字
                "pic": item['pic'],                                                 # 图片
                "price": item['price'],                                             # 价格
                "monthSellCountFuzzyString": item['monthSellCountFuzzyString'],     # 月售
                "provcity": item['provcity'],                                       # 产地
                "item_id": item['itemId'],                                          # itemId
            }
            dict2 = self.get_detail(item['itemId'])
            dict1.update(dict2)

            commodity_information_list.append(dict1)
            print(dict1)
        print(commodity_information_list, len(commodity_information_list))
        return commodity_information_list

    def get_detail(self, item_id="611658999337"):
        """
        获取商品详细信息:
        Returns:

        """
        response = requests.get(
            f'https://item.taobao.com/item.htm?id={item_id}&ali_refid=a3_430582_1006:1110306571:N:emtiAWsF8%2Bzhhxaiwzc0Aw%3D%3D:2217fe1dd3fb55ad9851f45c3c3444f1&ali_trackid=1_2217fe1dd3fb55ad9851f45c3c3444f1&spm=a21n57.1.0.0',
            cookies=self.cookies, headers=self.headers)
        html = response.text
        # print(html, f'https://item.taobao.com/item.htm?id={item_id}&ali_refid=a3_430582_1006:1110306571:N:emtiAWsF8%2Bzhhxaiwzc0Aw%3D%3D:2217fe1dd3fb55ad9851f45c3c3444f1&ali_trackid=1_2217fe1dd3fb55ad9851f45c3c3444f1&spm=a21n57.1.0.0')
        soup = BeautifulSoup(html, "html.parser")
        attributes_html = soup.findAll("ul", attrs={"class": "attributes-list"})

        details = {}
        pattern_style = r'风格:\s(.*?)\n'
        pattern_applicable_age = r'年龄:\s(.*?)\n'
        pattern_fabric = r'面料.*?:\s(.*?)\n'
        pattern_season = r'季节:\s(.*?)\n'

        if attributes_html:
            attributes_html = attributes_html[0].text

            details = {
                "style": re.findall(pattern_style, attributes_html)[0]
                if re.findall(pattern_style, attributes_html) else None,

                "applicable_age": re.findall(pattern_applicable_age, attributes_html)[0]
                if re.findall(pattern_applicable_age, attributes_html) else None,

                "fabric": re.findall(pattern_fabric, attributes_html)[0]
                if re.findall(pattern_fabric, attributes_html) else None,

                "season": re.findall(pattern_season, attributes_html)[0]
                if re.findall(pattern_season, attributes_html) else None,
            }

            # print(details)

        return details

    @staticmethod
    def parse_json_from_string(json_string):
        """
        将字符串转换为 JSON
        Args:
            json_string:

        Returns:

        """
        try:
            match = re.search(r'mtopjsonp\d+\((.*?)\)', json_string)

            if match:
                json_str = match.group(1)
                # 将 JSON 字符串解析为字典
                parsed_json = json.loads(json_str)

                return parsed_json
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误：{e}")
            return None

    @staticmethod
    def data_to_db(data):
        """

        Args:
            data:

        Returns:

        """
        # Todo 写解析出来的数据存到数据库里
        ...


if __name__ == '__main__':
    crawl_taobao = CrawlTaoBao()
    print(f"cookie>>>>>>:\n{crawl_taobao.cookies}\n")
    # crawl_taobao.get_detail("640513959729")
    # crawl_taobao.search_commodity("衣服", 1, 60)
    crawl_taobao.search_commodity("女装")
    # print(crawl_taobao.get_detail("702507248639"))
    # print(content)
    # detail=[]
    # for itemid in itemId:
    #     print(itemid)
    #     detail.append(crawl_taobao.get_detail(itemid))
    # print(detail)
