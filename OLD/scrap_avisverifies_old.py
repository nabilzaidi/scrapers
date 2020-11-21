from lxml import html
import requests
import json
import pandas as pd
from unidecode import unidecode
from time import sleep
import re
from datetime import datetime
from urllib.parse import (
        urlencode, unquote, urlparse, parse_qsl, ParseResult
    )

import sys
sys.path.append("../..")
from scrap_app import cache_set

def clean_xpath_res(l):
    return unidecode("\n".join(l).strip())

def _aux_clean_number(number_text):
    return int(number_text[0])

class AvisVerifiesScraper:
    def __init__(self, url, session_id, process):
        self.url = url
        self.n_reviews = None
        self.reviews = []
        self.session_id = session_id
        self.process = process
    
    def _parse_review(self, review_block):
        info = dict()
        xpath_rating = ".//span[@itemprop='ratingValue']//text()"
        info["rating_star"] = clean_xpath_res(review_block.xpath(xpath_rating))
        xpath_date = ".//meta[@itemprop='datePublished']/@content"
        info["date"] = str(review_block.xpath(xpath_date)[0])
        xpath_review = ".//div[@itemprop='reviewBody']//text()"
        info["review"] = clean_xpath_res(review_block.xpath(xpath_review))
        xpath_details = ".//div[@class='details suite']//text()"
        info["details_hide"] = clean_xpath_res(review_block.xpath(xpath_details))
        return info

    def clean_review(self, r):
        cleaned_r = r.copy()
        cleaned_r["rating_star_cleaned_hide"] = _aux_clean_number(cleaned_r["rating_star"])
        # df_cleaned["date_month"] = pd.DatetimeIndex(df_cleaned["date"]).month
        # df_cleaned["date_year"] = pd.DatetimeIndex(df_cleaned["date"]).year
        cleaned_r["date_year_month_hide"] = f"{cleaned_r['date'][-4:]}-{cleaned_r['date'][3:5]}"
        cleaned_r["text_cleaned_hide"] = cleaned_r["review"].replace("[^a-zA-Z#]", " ").lower()

        return cleaned_r
        
    def _parse_page(self, page):
        info = list()
        reviews = page.xpath("//div[@class='review row']")
        for r in reviews:
            res = self._parse_review(r)
            info.append(self.clean_review(res))
        return info
    
    def _url_page(self, n_page):
        return f"{self.url}?p={n_page}"

    def current_page(self, url):
        page_argument = "p"
        parsed_get_args = dict(parse_qsl(urlparse(unquote(url)).query))
        return int(parsed_get_args.get(page_argument, 1))

    def _next_url(self, url):
        page_argument = "p"
        # Unquoting URL first so we don't loose existing args
        url = unquote(url)
        # Extracting url info
        parsed_url = urlparse(url)
        # Extracting URL arguments from parsed URL
        get_args = parsed_url.query
        # Converting URL arguments to dict
        parsed_get_args = dict(parse_qsl(get_args))
        parsed_get_args[page_argument] = int(parsed_get_args.get(page_argument, 1)) + 1
        # Converting URL argument to proper query string
        encoded_get_args = urlencode(parsed_get_args, doseq=True)
        # Creating new parsed result object based on provided with new
        # URL arguments. Same thing happens inside of urlparse.
        new_url = ParseResult(
            parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            parsed_url.params, encoded_get_args, parsed_url.fragment
        ).geturl()
        print("next_url", new_url)
        return new_url
    
    def _get_html(self, url):
        page_content = requests.get(url).content
        page_html = html.fromstring(page_content)
        return page_html

    def scrap_n_reviews(self):
        page_html = self._get_html(self.url)
        xpath_n_reviews = "//span[@class='count']//text()"
        n_reviews_str = re.sub("[^0-9]", "", page_html.xpath(xpath_n_reviews)[0])
        self.n_reviews = int(n_reviews_str.replace(" ", ""))
    
    def get_n_pages(self):
        page_html = self._get_html(self.url)
        xpath_pages = "//select[@class='selectPage']/option"
        list_pages = page_html.xpath(xpath_pages)
        n_pages = len(list_pages)
        return n_pages
    
    def scrap_reviews(self):
        cache_set("scrapping_progress_website", "Starting to scrap...", self.session_id)
        n_pages = self.get_n_pages()
        url = self.url
        n_start = self.current_page(url)
        for n in range(n_start, n_pages + 1):
            page_html = self._get_html(url)
            page_info = self._parse_page(page_html)
            for i in page_info:
                i["page"] = n
            self.reviews += page_info
            cache_set("scrapping_progress_website", f"Done with {url}", self.session_id)
            cache_set("scrapping_progress_percent", f"{int( (n - n_start + 1) / (n_pages - n_start + 1) * 100)}", self.session_id)
            if not page_html.xpath("//a[@rel='next']/@href"):
                break
            if n % 1000 == 0:
                sleep(25)
            elif n % 100 == 0:
                sleep(5)
            elif n % 10 == 0:
                sleep(1)
            url = self._next_url(url)
            if self.process.is_aborted():
                print("process aborted", self.session_id)
                break
        cache_set("scrapping_progress_percent", f"100", self.session_id)
    
    def scrap_website(self):
        self.scrap_n_reviews()
        self.scrap_reviews()
        res = self.__dict__
        del res["process"]
        return res


# def clean_data(df):
#     df_cleaned = df.copy()
#     df_cleaned["rating_star_cleaned_hide"] = df["rating_star"].apply(_aux_clean_number)
#     # df_cleaned["date_month"] = pd.DatetimeIndex(df_cleaned["date"]).month
#     # df_cleaned["date_year"] = pd.DatetimeIndex(df_cleaned["date"]).year
#     df_cleaned["date_year_month_hide"] = pd.to_datetime(df_cleaned["date"], format="%d/%m/%Y").dt.strftime('%Y-%m')
#     df_cleaned["text_cleaned_hide"] = df_cleaned["review"].str.replace("[^a-zA-Z#]", " ").str.lower()

#     return df_cleaned
    
    
def scrap_reviews_avisverifies(url, session_id, process):
    avs = AvisVerifiesScraper(url, session_id, process)
    info = avs.scrap_website()
    # df = pd.DataFrame(info)
    # df = df.drop_duplicates(["rating_star", "date", "review"])
    # df = clean_data(df)
    # df = df.reset_index()
    # if filename_save:
    #     df.to_csv(filename_save, encoding="utf-8")
    # return df.to_dict(orient="records")
    return info
