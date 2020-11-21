import sys
sys.path.append("../..")
from reviews.scrapers.scraper_tools import ReviewScraper, clean_xpath_res, _aux_clean_number
import json
import re
from selenium import webdriver


GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.binary_location = GOOGLE_CHROME_PATH


class IgraalScraper(ReviewScraper):
    def __init__(self, url, session_id, process):
        page_argument = "page"
        super().__init__(url, session_id, process, page_argument)
        self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
        # self.driver = webdriver.Chrome(options=chrome_options)

    def _get_html(self, url):
        page_content = self.driver.get(url).page_source
        page_html = html.fromstring(page_content)
        return page_html

    def _split_args_url(self, url):
        base = "https://fr.igraal.com/avis/"
        args = url[len(base):]
        l_args = args.split("/")
        company = l_args[0]
        if len(l_args) > 1 and len(l_args[1]) > 0:
            try:
                page = int(l_args[1])
            except:
                page = 1
        else:
            page = 1
        return {
            "base": base,
            "company": company,
            "page": page,
            "url": url,
            "cleaned_url": f"{base}{company}/{page}"
        }

    def _current_page(self, url):
        return self._split_args_url(url)["page"]

    def _next_url(self, url):
        # Unquoting URL first so we don't loose existing args
        dict_args = self._split_args_url(url) 
        next_page = dict_args["page"] + 1
        base = dict_args["base"]
        company = dict_args["company"]

        new_url = f"{base}{company}/{next_page}"
        return new_url
    
    def _parse_review(self, review_block):
        info = dict()
        xpath_reviewer = ".//figcaption[@class='review__left-txt-wrap']//text()"
        info["reviewer_hide"] = clean_xpath_res(review_block.xpath(xpath_rating))
        xpath_rating = ".//strong[contains(@class, 'review__note')]//text()"
        info["rating_star"] = clean_xpath_res(review_block.xpath(xpath_rating))
        xpath_date = ".//strong[contains(@class, 'review__header-date')]//text()"
        info["date"] = clean_xpath_res(review_block.xpath(xpath_date))
        xpath_title = ".//strong[contains(@class, 'review__title')]//text()"
        info["title"] = clean_xpath_res(review_block.xpath(xpath_title))
        xpath_review = ".//p[contains(@class, 'review__desc')]//text()"
        info["review"] = clean_xpath_res(review_block.xpath(xpath_review))
        
        xpath_detailed_rating = ".//div[@class='review__detail-rating-wrap']"
        list_detailed_rating = review_block.xpath(xpath_detailed_rating)
        for rating_block in list_detailed_rating:
            rating_name = clean_xpath_res(rating_block.xpath(".//span[@class='review__detail-rating']"))
            n_stars = len(rating_block.xpath(".//polygon[contains(@class, 'star-active')]"))/2
            info[f"rating_{rating_name}"] = n_stars
        return info

    def clean_review(self, r):
        cleaned_r = r.copy()
        cleaned_r["rating_star_cleaned_hide"] = _aux_clean_number(r["rating_star"])
        cleaned_r["date_year_month_hide"] = cleaned_r["date"][3:]
        cleaned_r["text_cleaned_hide"] = f"{cleaned_r['title']} {cleaned_r['review']}"
        cleaned_r["text_cleaned_hide"] = cleaned_r["text_cleaned_hide"].replace("[^a-zA-Z#]", " ").lower()
        return cleaned_r

    def _parse_page(self, page):
        info = list()
        reviews = page.xpath("//article[contains(@class , 'review__item')]")
        for r in reviews:
            res = self._parse_review(r)
            info.append(self.clean_review(res))
        return info

    def scrap_n_reviews(self):
        page_html = self._get_html(self.url)
        xpath_n_reviews = "//div[@class='review-page__subtitle-wrap']/h2[contains(@class, 'review__subtitle')]//text()"
        n_reviews_str = re.sub("[^0-9]", "", page_html.xpath(xpath_n_reviews)[0])
        self.n_reviews = int(n_reviews_str.replace(" ", ""))
    
    def get_n_pages(self):
        n_pages = self.n_reviews // 50 + 1 # 20 reviews per page
        # Not optimised, it's the max # of pages, but often less
        return n_pages

    def is_last_page(self, page):
        return len(page.xpath("//li[contains(@class, 'pagination__item--last')]")) == 0


def scrap_reviews_igraal(url, session_id, process):
    igs = IgraalScraper(url, session_id, process)
    info = igs.scrap_website()
    return info
