from lxml import html
import requests
from unidecode import unidecode
from time import sleep
from urllib.parse import (
        urlencode, unquote, urlparse, parse_qsl, ParseResult
    )


def clean_xpath_res(l):
    return unidecode("\n".join(l).strip())

def _aux_clean_number(number_text):
    return int(number_text[0])

class ReviewScraper:
    def __init__(self, url, page_argument):
        self.url = url
        self.n_reviews = None
        self.reviews = []
        self.page_argument = page_argument

    def _current_page(self, url):
        parsed_get_args = dict(parse_qsl(urlparse(unquote(url)).query))
        return int(parsed_get_args.get(self.page_argument, 1))

    def _next_url(self, url):
        # Unquoting URL first so we don't loose existing args
        url = unquote(url)
        # Extracting url info
        parsed_url = urlparse(url)
        # Extracting URL arguments from parsed URL
        get_args = parsed_url.query
        # Converting URL arguments to dict
        parsed_get_args = dict(parse_qsl(get_args))
        parsed_get_args[self.page_argument] = int(parsed_get_args.get(self.page_argument, 1)) + 1
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
    
    def _parse_review(self, review_block):
        return dict()

    def clean_review(self, review):
        return dict()

    def _parse_page(self, page):
        return []

    def scrap_n_reviews(self):
        return 0
    
    def get_n_pages(self):
        return 0

    def is_last_page(self, page):
        return True

    def _pause(self, n):
        if n % 1000 == 0:
            time_sleep = 25
        elif n % 100 == 0:
            time_sleep = 7
        elif n % 10 == 0:
            time_sleep = 1
        else:
            time_sleep = 0

        if self.n_reviews > 10000:
            time_sleep = 3 * time_sleep + 1
        elif self.n_reviews > 1000:
            time_sleep *= 2

        if time_sleep > 5:
            print(f"Sleeping for {time_sleep}sec to avoid being blocked")
        if time_sleep:
            sleep(time_sleep)
    
    def scrap_reviews(self):
        print("Starting to scrap...")
        
        n_pages = self.get_n_pages()
        url = self.url
        n_start = self._current_page(url)
        for n in range(n_start, n_pages + 1):
            page_html = self._get_html(url)
            page_info = self._parse_page(page_html)
            for i in page_info:
                i["page"] = n
            self.reviews += page_info
            
            print(f"Done with {url}")
            n_done = (n - n_start + 1)
            n_total = (n_pages - n_start + 1)
            percent_done = int( n_done / n_total * 100)
            print(f"Done {n_done}/{n_total} ({percent_done}%)")

            if self.is_last_page(page_html):
                break
            self._pause(n - n_start + 1)
            url = self._next_url(url)
    
    def scrap_website(self):
        self.scrap_n_reviews()
        self.scrap_reviews()
        res = {
        	"url": self.url,
        	"n_reviews": self.n_reviews,
        	"reviews": self.reviews
        }
        return res
