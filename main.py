# (c) @AbirHasan2005

import re
import json
import requests
from bs4 import BeautifulSoup


class AmazonDealsScraper:
    def __init__(self, deals_page_link: str = "https://www.amazon.com/gp/goldbox?ref_=nav_cs_gb"):
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
        for count, raw_data in enumerate(self.deals_raw_json_data):
            title = raw_data["entity"]["details"]["entity"]["title"]
            deal_type = raw_data["entity"]["details"]["entity"]["type"]
            link = "https://www.amazon.com" + raw_data["entity"]["details"]["entity"]["landingPage"]["url"]
            print(f"{count+1}. Checking [{link}] ...")
            with requests.Session() as session:
                session.headers.update(
                    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                                   "Chrome/106.0.0.0 "
                                   "Safari/537.36"}
                )
                response = session.get(link)
            soup = BeautifulSoup(response.content, "lxml")
            deal_not_available_element = soup.find("div", attrs={"class": "a-container"})
            if deal_not_available_element and (
                    "This deal is currently unavailable, but you can find more great deals on our Today’s Deals page."
                    in deal_not_available_element.text
            ):
                continue
            deals_elements = soup.find_all(
                "li", attrs={
                    "class": "a-list-normal a-spacing-none no-margin-right overflow-hidden octopus-response-li-width"
                }
            )
            for deal_element in deals_elements:
                title = deal_element.find(
                    "a", attrs={"class": "a-size-base a-color-base a-link-normal a-text-normal"}
                ).text.replace("\n", "").strip()
                link_anker = deal_element.find("a", attrs={"class": "a-link-normal"})
                link = "https://amazon.com" + link_anker.get("href", "").split("?", 1)[0] + "?&linkCode=ll1&tag=jeanpat-20&linkId=b293a26b1a435a150de833463e955114&language=en_US&ref_=as_li_ss_tl"
                data = {"title": title, "deal_type": deal_type, "link": link}
                if with_price:
                    try:
                        price_data = soup.find("div", attrs={"class": "a-row octopus-dlp-price"})
                        price = price_data.find("span", attrs={"class": "a-price-whole"}).text.replace(".", ' ')
                        saving_info = price_data.find("span", attrs={"class": "octopus-widget-price-saving-info"}).find(
                            "span", attrs={
                                "class": "a-size-mini a-color-tertiary octopus-widget-strike-through-price a-text-strike"
                            }
                        ).text.replace("\n", "").strip()
                        price_data = f"Price: {price}, List Price: {saving_info}"
                    except:
                        price_data = ""
                    data["price_data"] = price_data
                self.deals.append(data)
        return self.deals


amazon_deals = AmazonDealsScraper().parse_deals(True)
print(amazon_deals)
