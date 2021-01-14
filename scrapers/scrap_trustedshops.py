
from .scraper_tools import ReviewScraper, clean_xpath_res, _aux_clean_number
import json
import re


class TrustedShopsScraper(ReviewScraper):
    def __init__(self, url):
        page_argument = "page"
        super().__init__(url=url,
                        page_argument=page_argument)
    
    def _parse_review(self, review_block):
        info = dict()
        xpath_rating = ".//span[contains(@class, 'tsproi-star-filled active')]"
        info["rating_star"] = str(len(review_block.xpath(xpath_rating)))
        xpath_date = ".//review-header//text()"
        info["date"] = clean_xpath_res(review_block.xpath(xpath_date))
        xpath_review = ".//loading-line[1]//text()"
        info["review"] = clean_xpath_res(review_block.xpath(xpath_review))
        xpath_is_verified_info = ".//loading-line[2]//text()"
        info["is_verified_hide"] = clean_xpath_res(review_block.xpath(xpath_is_verified_info))
        xpath_review_answer = ".//review-answer/div/div[2]//text()"
        info["review_answer_hide"] = clean_xpath_res(review_block.xpath(xpath_review_answer))
        return info

    def clean_review(self, r):
        cleaned_r = r.copy()
        cleaned_r["rating_star_cleaned_hide"] = _aux_clean_number(r["rating_star"])
        cleaned_r["date_year_month_hide"] = cleaned_r["date"]
        cleaned_r["text_cleaned_hide"] = f"{cleaned_r['review']}"
        cleaned_r["text_cleaned_hide"] = cleaned_r["text_cleaned_hide"].replace("[^a-zA-Z#]", " ").lower()
        return cleaned_r

    def _parse_page(self, page):
        info = list()
        reviews = page.xpath("//review")
        for r in reviews:
            res = self._parse_review(r)
            info.append(self.clean_review(res))
        return info

    def scrap_n_reviews(self):
        page_html = self._get_html(self.url)
        xpath_n_reviews = "//div[contains(@class, 'total-rating-count')]//text()"
        n_reviews_str = re.sub("[^0-9]", "", page_html.xpath(xpath_n_reviews)[0])
        self.n_reviews = int(n_reviews_str.replace(" ", "").replace(".", ""))
    
    def get_n_pages(self):
        n_pages = self.n_reviews // 20 + 1 # 20 reviews per page
        # Not optimised, it's the max # of pages, but often less
        return n_pages

    def is_last_page(self, page):
        return len(page.xpath("//div[@page-index='next']")) == 0


def scrap_reviews_trustedshops(url):
    tss = TrustedShopsScraper(url)
    info = tss.scrap_website()
    return info
