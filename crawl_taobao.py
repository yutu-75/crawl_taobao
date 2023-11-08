import time
import hashlib
import requests
from fake_useragent import UserAgent


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

        self.cookies = {
            # 'isg': 'BB0dLh-OJPY-dsDauvWnwbDTLPkXOlGM_8mxTN_iXnSjlj3Ip4sZXOGAwIqQDmlE',
        }
        self.get_token()

    def search_commodity(self, name="女装", page_count=0, page_size=60):
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
        print(response.text)

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

    def get_token(self) -> None:
        """
        获取访问接口的token
        Returns:

        """
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


if __name__ == '__main__':
    crawl_taobao = CrawlTaoBao()

    print(crawl_taobao.cookies)
    crawl_taobao.search_commodity("衣服")
    time.sleep(3)
    crawl_taobao.search_commodity("衣服", 1, 60)
