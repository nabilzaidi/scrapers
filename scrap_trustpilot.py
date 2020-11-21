
from scrapers.scraper_tools import ReviewScraper, clean_xpath_res, _aux_clean_number
import json
import re


class TrustpilotScraper(ReviewScraper):
    def __init__(self, url):
        page_argument = "page"
        super().__init__(url, page_argument)
    
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

    def scrap_n_reviews(self):
        page_html = self._get_html(self.url)
        xpath_n_reviews = "//h2[@class='header--inline']//text()"
        n_reviews_str = re.sub("[^0-9]", "", page_html.xpath(xpath_n_reviews)[0])
        self.n_reviews = int(n_reviews_str.replace(" ", "").replace(".", ""))
    
    def get_n_pages(self):
        n_pages = self.n_reviews // 20 + 1 # 20 reviews per page
        # Not optimised, it's the max # of pages, but often less
        return n_pages

    def is_last_page(self, page):
        return len(page.xpath("//a[@data-page-number='next-page']")) == 0


def scrap_reviews_truspilot(url):
    tps = TrustpilotScraper(url)
    info = tps.scrap_website()
    return info
