import json
import os
import re
import time
import hashlib
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd

from configurations import config
from db.redis.redis_data_client import RedisClient
from urllib.parse import urlparse, parse_qs


class CrawlTaoBao:
    def __init__(self):
        self.redis_client = RedisClient()
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
            'user-agent': UserAgent().random  # 随机生成一个User-Agent
        }

        # Todo ["cna","sgcookie"] 生成方法没写, 待写...
        self.cookies = {

            # 'cna': 'fHKVHZ23KEMCARsLEYfFlegU',
            # 'sgcookie': 'E100fRiNqBPwDU36l9G1AiXsLbBcnOLqqJ1Xu%2BgWIgP2r%2B1s6bw8jOLpFJEmWTcWhCFSLVHJeetttNAZdmAQRDy4AEOzBLFohJpDVTHik4ifkJICcS7JFQ5AqZUQp1gyC%2Fmc',
            'cna': 'fHKVHZ23KEMCARsLEYfFlegU',
            'sgcookie': 'E100fRiNqBPwDU36l9G1AiXsLbBcnOLqqJ1Xu%2BgWIgP2r%2B1s6bw8jOLpFJEmWTcWhCFSLVHJeetttNAZdmAQRDy4AEOzBLFohJpDVTHik4ifkJICcS7JFQ5AqZUQp1gyC%2Fmc',
            # 'x5sec': '7b22617365727665723b32223a226133336563663764393133633035316461363835636264616561653338353538434a375974366f47454e4f786e6f6a352f2f2f2f2f774561444449334e7a67344d5455334e5467374e5443516f6357652b2f2f2f2f2f384251414d3d222c22733b32223a2235633535616530396134343065303537227d',
            'x5sec': '7b22617365727665723b32223a223163643963643630376133336634653030316635336539383261393064613632434c7678794b6f47454e4f61774d48362f2f2f2f2f774561444449334e7a67344d5455334e5467374e4443516f6357652b2f2f2f2f2f384251414d3d222c22733b32223a2233303538376262316137373061366531227d; tfstk=duxHEox9Ie7CU_1HlXIIYkbrZk3TAWs5aQERwgCr7156puHBpFXywCMSdMpPZQAO1pE-',

        }

        self.update_cookies()
        self.create_folder_if_not_exists()

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

    @staticmethod
    def create_folder_if_not_exists(folder_path="images"):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"文件夹 '{folder_path}' 创建成功！")
        else:
            print(f"文件夹 '{folder_path}' 已存在，无需创建。")

    def download_img(self, url):
        """
        下载图片
        Args:
            url:

        Returns:

        """
        img_name = url.split("/")[-1]
        response = requests.get(url, cookies=self.cookies, headers=self.headers)

        if response.status_code == 200:
            with open(f"images/{img_name}.jpg", 'wb') as file:
                file.write(response.content)
            return url

    def search_commodity(self, name="女装", page_count=1, page_size=48):
        """
        Args:
            name:

        Returns:
        :param name:
        :param page_count:
        :param page_size:

        """

        data = str({
            "appId": "34385",
            "params": f'{{"device":"HMA-AL00","isBeta":"false","grayHair":"false","from":"nt_history","brand":"HUAWEI","info":"wifi","index":"4","rainbow":"","schemaType":"auction","elderHome":"false","isEnterSrpSearch":"true","newSearch":"false","network":"wifi","subtype":"","hasPreposeFilter":"false","prepositionVersion":"v2","client_os":"Android","gpsEnabled":"false","searchDoorFrom":"srp","debug_rerankNewOpenCard":"false","homePageVersion":"v7","searchElderHomeOpen":"false","search_action":"initiative","sugg":"_4_1","sversion":"13.6","style":"list","ttid":"600000@taobao_pc_10.7.0","needTabs":"true","areaCode":"CN","vm":"nw","countryNum":"156","m":"pc","page":{page_count},"n":{page_size},"q":"{name}","tab":"all","pageSize":"{page_size}","totalPage":"100","totalResults":"141297","sourceS":"0","sort":"_coefp","bcoffset":"-3","ntoffset":"3","filterTag":"","service":"","prop":"","loc":"","start_price":null,"end_price":null,"startPrice":null,"endPrice":null}}'
        })
        params = {
            'jsv': '2.6.2',
            'appKey': self.app_key,
            't': self.t,
            'sign': self.get_sign(data),
            'api': 'mtop.relationrecommend.WirelessRecommend.recommend',
            'v': '2.0',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp2',
            'data': data
        }

        response = requests.get(
            'https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/',
            params=params,
            cookies=self.cookies,
            headers=self.headers,
        )

        response_data = response.json()

        return response_data

    def get_detail_taobao(self, item_url):
        """
        获取商品详细信息:
        Returns:

        """
        # TODO 天猫页面的爬虫没有写
        # https://detail.tmall.com/item.htm?abbucket=0&id=726611072140&ns=1&sku_properties=1627207:1553005176
        response = requests.get(
            item_url,
            cookies=self.cookies, headers=self.headers)
        html = response.text

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

    def get_detail_tianmao(self, item_url, item_id=None):

        parsed_url = urlparse(item_url)
        query_parameters = parse_qs(parsed_url.query)
        item_id = query_parameters.get('id') if query_parameters.get('id') else item_id
        abbucket = query_parameters.get('abbucket')
        ns = query_parameters.get('ns')
        data = str({
            "id": item_id,
            "detail_v": "3.3.2",
            "exParams": str({
                "abbucket": abbucket,
                "id": item_id,
                "ns": f"{query_parameters.get('ns')}",
                "queryParams": f"abbucket={abbucket}&id={item_id}&ns={ns}",
                "domain": "https://detail.tmall.com",
                "path_name": "/item.htm"})
        })
        params = {
            'jsv': '2.6.2',
            'appKey': self.app_key,
            't': self.t,
            'sign': self.get_sign(data),
            'api': 'mtop.relationrecommend.WirelessRecommend.recommend',
            'v': '2.0',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp2',
            'data': data
        }
        response = requests.get(
            'https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/',
            params=params,
            cookies=self.cookies,
            headers=self.headers,
        ).text
        response_data = self.parse_json_from_string(response)

        details = {
            "season": None,
            "style": None,
            "fabric": None,
            "applicable_age": None,

        }
        # print(response)
        response_data_details = response_data["data"]["props"]["groupProps"][-1]["基本信息"]

        for i_dict in response_data_details:
            key = list(i_dict.keys())[0]
            if '季节' in key:
                details["season"] = i_dict[key]
            elif '风格' in key:
                details["style"] = i_dict[key]
            elif '面料' in key or '材质' in key:
                details["fabric"] = i_dict[key]
            elif '年龄' in key:
                details["applicable_age"] = i_dict[key]
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

            else:
                parsed_json = json.loads(json_string)
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

    def data_to_redis(self, data):

        data = data['data']["itemsArray"]
        commodity_information_list = []
        for item in data:
            dict1 = {
                "item_name": item['title'],  # 衣服名字
                "pic": item['pic_path'],  # 图片
                "price": item['price'],  # 价格
                "real_sales": item['realSales'],  # 月售
                "procity": item['procity'],  # 产地
                "item_id": item['item_id'],  # item_id
                "item_url": "https:" + item["auctionURL"] if "https" not in item["auctionURL"] else item["auctionURL"],
                # itemId

            }
            if self.redis_client.json_get(dict1["item_id"]):
                continue

            detail = self.get_detail_taobao(dict1['item_url'])

            if detail:
                dict2 = detail
                print("这是 淘宝 页面!!!")
            else:
                print("这是 天猫 页面!!!")
                dict2 = self.get_detail_tianmao(dict1['item_url'], dict1['item_id'])

            dict1.update(dict2)
            if dict2:
                self.redis_client.json_set(dict1["item_id"], dict1)
            print(
                f"详细信息:{dict2},获取不到详细信息,请去点击item_url查看原因或者修改get_detail方法. \n完整信息:{dict1}\n")

        return commodity_information_list

    def get_redis_keys(self):
        """
        获取redis里所有的key
        Returns:

        """
        return self.redis_client.keys(f"{config.get('house', 'house_name')}*")

    def get_redis_data(self):
        """
        获取redis数据库里全部的数据.
        Returns:

        """

        result_list = []
        for key in self.get_redis_keys():
            value = self.redis_client.json_get(key)
            print(value)
            result_list.append(value)

        # 将JSON数据转换为DataFrame
        df = pd.json_normalize(result_list)
        # 将DataFrame保存为CSV文件
        df.to_csv('output_csv_file.csv', index=False, encoding='utf-8')
        return result_list


if __name__ == '__main__':
    crawl_taobao = CrawlTaoBao()
    print(f"cookie>>>>>>:\n{crawl_taobao.cookies}\n")

    # crawl_taobao.download_img('https://img.alicdn.com/imgextra/i1/31774561/O1CN01HHHX5d1jYzBhuQx7Z_!!0-saturn_solar.jpg')
    # print(crawl_taobao.get_detail_taobao('https://click.simba.taobao.com/cc_im?p=%C5%AE%D7%B0&s=1709035793&k=845&e=v9sz85SYZ5A0JfADfC6GWNxq5XLbBhQqVkRa8TNEc9IGOLJ5waFYhr5iyOqoaigMotelTNSsD6OCpx7zDFWcEPpIPHv0qsIfM2tOEc0D1gibkb9DnRz6VneSKZQTAavpB2Txvn0h9zleCi6NAhmKNzx%2FQU1Tp6q3cHvoApmO7DaIqUUqzt8KYojv3nPbxRjrEwULzM%2BQCI2kb%2FwbG5zQ9F8G6TwsUX7GbaDNN2nPTZu7JkSqBObwtK9EYydVOmgLYoxzDnOQDPMUbLAJ1Q7wWZ8lKKwdJrktpDcwnHrMIMtdsljuu0gFXZsiXrgHYzizzGXd%2FPULTQkddGmv%2FEKpBSsmKBt%2FpTo66%2Fyo3i3EGJZfDklV%2F%2BL82BSQ3SyRWOUnWhIrW0TCNZF9pzA4bRPxmk8RR1ro3LNohJKxWlNM%2Bg8rtiA7WGYkxbIon1wABBlauAFaNoZvkA1Xi3qqaETRE1Edu9rX%2Bn6NXwCdbKJbygxW7zJ7DBceY1D5Ed2ivtUZhyiDkI3cbCxLTqWB3lm2EzEkpa9HDCwGjy0csr5IR9C1jx4fMUdjwmeD2wc27UPPD5xHP5FqpNhsnMf23niJaNdwOHosLhwc8PqLrOBs8FgC0BvNnAStPNcFnvAIbBG9oplUFNPjCnXFBy8jE8vS39%2FR3JTOQseoqL%2BypBSzrnFzTuIgYVouD5Dy08icAZr1LNzKt3lzp6hkKIh3HpEephoGoJjFB69EC5QBK3XeVEQ8Sxr67zuEW6zgOqtty8rYF0zFzBKnKIiKn0NEfWlBien6iz1NxWZIX67uFDTqTAsZFQ1O8aijFixj2GxdCR%2BYNdfOJB5mj8k%3D#detail'))
    # print(len(crawl_taobao.redis_client.keys("crawl_taobao*")))
    # crawl_taobao.get_detail_tianmao("https://detail.tmall.com/item.htm?id=654566291507&ns=1&abbucket=0")
    for i in range(2500, 5000):
        print(f"第{i}页码")
        result = crawl_taobao.search_commodity("女装", i, 48)
        crawl_taobao.data_to_redis(result)

    # 获取redis数据
    # print(len(crawl_taobao.get_redis_data()))
    # print(crawl_taobao.get_redis_keys(), len(set(crawl_taobao.get_redis_keys())))
