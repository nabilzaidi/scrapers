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

class TrustpilotScraper:
    def __init__(self, url, session_id, process):
        self.url = url
        self.n_reviews = None
        self.reviews = []
        self.session_id = session_id
        self.process = process
    
    def _parse_review(self, review_block):
        info = dict()
        xpath_rating = ".//div[@class='star-rating star-rating--medium']/img/@alt"
        info["rating_star"] = clean_xpath_res(review_block.xpath(xpath_rating))
        xpath_date = ".//div[@class='review-content-header__dates']/script/text()"
        info["date"] = json.loads(review_block.xpath(xpath_date)[0])["publishedDate"]
        xpath_title = ".//h2[@class='review-content__title']//text()"
        info["title"] = clean_xpath_res(review_block.xpath(xpath_title))
        xpath_review = ".//p[@class='review-content__text']//text()"
        info["review"] = clean_xpath_res(review_block.xpath(xpath_review))
        xpath_n_reviews = ".//div[@class='consumer-information__review-count']//text()"
        info["n_reviews_customer_hide"] = clean_xpath_res(review_block.xpath(xpath_n_reviews))
        xpath_is_verified_info = ".//div[contains(@class , 'review-verified')]//text()"
        is_verified_info = review_block.xpath(xpath_is_verified_info)
        if len(is_verified_info) > 1:
            is_verified_info = json.loads(is_verified_info[1])
        else:
            is_verified_info = dict()
        info["is_verified_hide"] = is_verified_info.get('isVerified', False)
        info["verification_source_hide"] = is_verified_info.get('verificationSource', "")
        info["review_source_hide"] = is_verified_info.get('reviewSourceName', "")
        # xpath_reply_date = ".//div[@class='brand-company-reply__date']/@datetime"
        # info["reply_date_hide"] = clean_xpath_res(review_block.xpath(xpath_reply_date))
        xpath_reply_content = ".//div[@class='brand-company-reply__content']//text()"
        info["reply_content_hide"] = clean_xpath_res(review_block.xpath(xpath_reply_content))
        return info

    def clean_review(self, r):
        cleaned_r = r.copy()
        cleaned_r["rating_star_cleaned_hide"] = _aux_clean_number(r["rating_star"])
        cleaned_r["n_reviews_customer_cleaned_hide"] = _aux_clean_number(r["n_reviews_customer_hide"])
        cleaned_r["date_year_month_hide"] = cleaned_r["date"][:7]
        cleaned_r["text_cleaned_hide"] = f"{cleaned_r['title']} {cleaned_r['review']}"
        cleaned_r["text_cleaned_hide"] = cleaned_r["text_cleaned_hide"].replace("[^a-zA-Z#]", " ").lower()
        return cleaned_r

    def _parse_page(self, page):
        info = list()
        reviews = page.xpath("//div[contains(@class , 'review-card')]")
        for r in reviews:
            res = self._parse_review(r)
            if res["rating_star"] != '#rating/desc/star0#':
                info.append(self.clean_review(res))
        return info
    
    def _url_page(self, n_page):
        return f"{self.url}?page={n_page}"

    def current_page(self, url):
        page_argument = "page"
        parsed_get_args = dict(parse_qsl(urlparse(unquote(url)).query))
        return int(parsed_get_args.get(page_argument, 1))

    def _next_url(self, url):
        page_argument = "page"
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
        return new_url

    
    def _get_html(self, url):
        page_content = requests.get(url).content
        page_html = html.fromstring(page_content)
        return page_html

    def scrap_n_reviews(self):
        page_html = self._get_html(self.url)
        xpath_n_reviews = "//h2[@class='header--inline']//text()"
        n_reviews_str = re.sub("[^0-9]", "", page_html.xpath(xpath_n_reviews)[0])
        self.n_reviews = int(n_reviews_str.replace(" ", ""))
    
    def get_n_pages(self):
        n_pages = self.n_reviews // 20 + 1 # 20 reviews per page
        # Not optimised, it's the max # of pages, but often less
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
            print(f"Done with {url}")
            if not page_html.xpath("//a[@data-page-number='next-page']"):
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
#     df_cleaned["n_reviews_customer_cleaned_hide"] = df["n_reviews_customer_hide"].apply(_aux_clean_number)
#     # df_cleaned["date_month"] = pd.DatetimeIndex(df_cleaned["date"]).month
#     # df_cleaned["date_year"] = pd.DatetimeIndex(df_cleaned["date"]).year
#     df_cleaned["date_year_month_hide"] = pd.to_datetime(df_cleaned["date"]).dt.strftime('%Y-%m')
#     df_cleaned["text_cleaned_hide"] = df_cleaned.apply(lambda x: f"{x['title']} {x['review']}", axis=1)
#     df_cleaned["text_cleaned_hide"] = df_cleaned["text_cleaned_hide"].str.replace("[^a-zA-Z#]", " ").str.lower()

#     return df_cleaned


def scrap_reviews_truspilot(url, session_id, process):
    tps = TrustpilotScraper(url, session_id, process)
    info = tps.scrap_website()
    return info
    # df = pd.DataFrame(info["reviews"])
    # print(df.shape)
    # df = df.drop_duplicates(["rating_star", "date", "title", "review"])
    # print(df.shape)
    # df = clean_data(df)
    # df = df.reset_index()
    # if filename_save:
    #     df.to_csv(filename_save, encoding="utf-8")
    # return df.to_dict(orient="records")

