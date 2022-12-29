# (c) @AbirHasan2005

import re
import json
import requests


class AmazonDealsScraper:
    def __init__(self, deals_page_link: str = "https://www.amazon.com/gp/goldbox"):
        self.deals = []
        with requests.Session() as session:
            session.headers.update(
                {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/106.0.0.0 "
                               "Safari/537.36"}
            )
            response = session.get(deals_page_link)
        soup = response.text
        assets = re.findall(r"assets\.mountWidget\(.*\)", soup)
        self.raw_json_data = json.loads(str(assets[0]).split("assets.mountWidget('slot-15', ", 1)[-1].rsplit(")", 1)[0])
        self.deals_raw_json_data = self.raw_json_data["prefetchedData"]["aapiGetDealsList"][0]["entities"]

    def parse_deals(self, with_price: bool = False):
        for raw_data in self.deals_raw_json_data:
            title = raw_data["entity"]["details"]["entity"]["title"]
            deal_type = raw_data["entity"]["details"]["entity"]["type"]
            link = "https://www.amazon.com" + raw_data["entity"]["details"]["entity"]["landingPage"]["url"]
            data = {"title": title, "deal_type": deal_type, "link": link}
            if with_price:
                try:
                    price_data = raw_data["entity"]["details"]["entity"]["price"]["details"]
                except KeyError:
                    price_data = {}
                data["price_data"] = price_data
            self.deals.append(data)
        return self.deals


amazon_deals = AmazonDealsScraper().parse_deals(True)
print(amazon_deals)
