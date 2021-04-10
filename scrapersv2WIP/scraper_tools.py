from lxml import html
import requests
from unidecode import unidecode
from time import sleep
from urllib.parse import (
        urljoin, urlencode, unquote, urlparse, parse_qsl, ParseResult
    )


def clean_xpath_res(l):
    return unidecode("\n".join(l).strip())

def _aux_clean_number(number_res):
    return int(number_res[0])


class ReviewScraper:
    def __init__(self, page_argument=None, next_page_xpath=""):
        self.page_argument = page_argument
        self.next_page_xpath = next_page_xpath

    def get_init_info(self, url):
        return dict()

    def _current_page(self, url):
        parsed_get_args = dict(parse_qsl(urlparse(unquote(url)).query))
        return int(parsed_get_args.get(self.page_argument, 1))

    def _next_url_page_argument(self, url):
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

    def _next_url_next_page(self, url, page_html):
        return urljoin(url, clean_xpath_res(page_html.xpath(self.next_page_xpath)))

    def _next_url(self, url=None, page_html=None):
        if self.page_argument is None:
            next_link = self._next_url_next_page(url, page_html)
        else:
            next_link = self._next_url_page_argument(url)
        return next_link

    
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

    def _pause(self, n, n_reviews):
        if n % 1000 == 0:
            time_sleep = 25
        elif n % 100 == 0:
            time_sleep = 7
        elif n % 10 == 0:
            time_sleep = 1
        else:
            time_sleep = 0

        if n_reviews > 10000:
            time_sleep = 3 * time_sleep + 1
        elif n_reviews > 1000:
            time_sleep *= 2

        if time_sleep > 5:
            print(f"Sleeping for {time_sleep}sec to avoid being blocked")
        if time_sleep:
            sleep(time_sleep)

    def logger(self, url, n_current, n_start, n_pages_max):
        print(f"Done with {url}")
        n_done = (n_current - n_start + 1)
        n_total = (n_pages_max - n_start + 1)
        percent_done = int( n_current / n_total * 100)
        print(f"Done {n_current}/{n_total} ({percent_done}%)")
    
    def _scrap_reviews_unique_url(self, url):
        print("Starting to scrap...")
        reviews = list()

        init_info = self.get_init_info(url)
        n_pages_max = init_info["n_pages_max"]

        n_start = self._current_page(url)

        for n in range(n_start, n_pages_max + 1):
            page_html = self._get_html(url)
            page_info = self._parse_page(page_html)
            for i in page_info:
                i["page"] = n
                i.update(init_info)
            reviews += page_info
            
            
            self.logger(url, n, n_start, n_pages_max)

            if self.is_last_page(page_html):
                break

            self._pause(n - n_start + 1, n_pages_max)
            url = self._next_url(url, page_html)

        return reviews

    def scrap_reviews(self, *list_urls):
    	reviews = []

    	for url in list_urls:
    		reviews += self._scrap_reviews_unique_url(url)

    	return reviews