import argparse
from pathlib import PurePath, Path
from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.firefox.firefox_profile import AddonFormatError
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from pathlib import Path
from urllib.parse import urlsplit
import json
import os
import sys
import time
import logging

class FirefoxProfileWithWebExtensionSupport(webdriver.FirefoxProfile):
    """
    Python's selenium bindings do not support the new Firefox WebExtension API
    Shim from https://intoli.com/blog/firefox-extensions-with-selenium/
    """

    def _addon_details(self, addon_path):
        try:
            return super()._addon_details(addon_path)
        except AddonFormatError:
            try:
                with open(os.path.join(addon_path, 'manifest.json'), 'r') as f:
                    manifest = json.load(f)
                    return {
                        'id': manifest['applications']['gecko']['id'],
                        'version': manifest['version'],
                        'name': manifest['name'],
                        'unpack': False,
                    }
            except (IOError, KeyError) as e:
                raise AddonFormatError(str(e), sys.exc_info()[2])


class WebsiteScraper(object):
    def __init__(self, gd_path, ffx_path, ext_path=None, show_browser=False):
        self.geckodriver_path = gd_path
        self.firefox_path = ffx_path
        self.extension_path = ext_path
        self.driver = None
        self.headless = not show_browser

        # Config constants
        self.crawler_config = {'page_load_timeout_secs': 20,
                               'num_timeout_retries': 3,
                               'scroll_pause_secs': 0.5}

    @staticmethod
    def normalizeUrl(url):
        """
        Normalize URLs to the format: scheme://netloc/path?query
        """
        parsed_url = urlsplit(url, allow_fragments=False)
        normalized_url = ""

        if parsed_url.scheme:
            normalized_url += parsed_url.scheme + "://"

        normalized_url += parsed_url.netloc + parsed_url.path

        if parsed_url.query:
            normalized_url += "?" + parsed_url.query

        return normalized_url

    def __startFfxDriver(self):
        """
        Configure the Firefox profile and start the web driver.
        """
        profile = FirefoxProfileWithWebExtensionSupport()
        profile.add_extension(self.extension_path)

        profile.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0")
        profile.set_preference("extensions.sdk.console.logLevel", "all")
        profile.set_preference("devtools.console.stdout.content", True)

        options = Options()
        options.headless = self.headless

        firefox_dev_binary = FirefoxBinary(self.firefox_path)
        self.driver = webdriver.Firefox(firefox_binary=firefox_dev_binary,
                                        firefox_profile=profile, executable_path=self.geckodriver_path, options=options)
        self.driver.set_page_load_timeout(
            self.crawler_config['page_load_timeout_secs'])

    def __scrollToBottom(self, max_scrolls=30):
        """
        Scroll to the bottom of the current page one viewport length at a time
        """
        scroll_height = -1
        try:
            while scroll_height != self.driver.execute_script("return window.pageYOffset"):
                scroll_height = self.driver.execute_script(
                    "return window.pageYOffset")
                self.driver.execute_script(
                    "window.scrollTo(0,{0}+window.innerHeight)".format(str(scroll_height)))
                time.sleep(self.crawler_config['scroll_pause_secs'])

                max_scrolls -= 1
                if max_scrolls == 0:
                    break
        except Exception as e:
            logging.warning("Couldn't scroll to bottom of page.")

    def __scrapePage(self, url):
        """
        Load a page andinteract with it as needed.
        """
        # Try to load the page, handling timeouts by retrying and eventually giving up
        attempt_num = 1
        while attempt_num <= self.crawler_config['num_timeout_retries']:
            if attempt_num > 1:
                logging.debug("Attempt #{1} for {0}...".format(
                    url, str(attempt_num)))
            else:
                logging.debug("Trying {0}".format(url))

            try:
                self.driver.get(url)
            except TimeoutException as e:
                logging.debug("Timed out getting {0}".format(url))
                attempt_num += 1
                continue
            except WebDriverException as e:
                logging.info("Error getting {0}: {1}".format(url, str(e)))
                break

            logging.info("Got {0}".format(url))
            break

        self.__scrollToBottom()
        time.sleep(30)

    def scrapePages(self, pages):
        """
        Navigate to each page in pages.
        """

        # Set up logging
        #log_path = str(Path(self.output_dir).joinpath("scrape.log"))
        #open(log_path, 'w')
        self.startAll()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                #logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )

        for page in pages:
            logging.info("Trying page {0}".format(page))
            self.__scrapePage(WebsiteScraper.normalizeUrl(page))

        self.stopAll()

    def startAll(self):
        self.__startFfxDriver()

    def stopAll(self):
        self.driver.quit()

parser = argparse.ArgumentParser(
    description='Scrape page contents for each page in the provided list.')
parser.add_argument('url_list', type=str,
                    help='The location of a text file containing a newline-delimited list of URLs')
parser.add_argument('-s', '--show_browser', action="store_true",
                    help="Show the browser UI while crawling")
parser.add_argument('-n', metavar='num_processes', type=int, default=2,
                    help="The number of simultaneous processes to run (default: %(default)s)")
parser.add_argument('-u', metavar='utils_dir', type=str, default="./utils",
                    help='The path to the folder where utilities, including the WebDriver, are stored (default: %(default)s)')
parser.add_argument('-f', metavar='firefox_path', type=str, default="./utils/firefox-dev",
                    help='The path to the Firefox Developer Edition binary (default: %(default)s)')

args = parser.parse_args()

if not Path(args.u).is_dir():
	raise argparse.ArgumentError(None, "Cannot access utilities directory {0}".format(args.u))
if not Path(args.url_list).is_file():
	raise argparse.ArgumentError(None, "Cannot access url list at {0}".format(args.url_list))

def runScraperProcess(pages):
    scraper = WebsiteScraper(
        gd_path = str(PurePath(args.u).joinpath("geckodriver")),
        ffx_path = str(PurePath(args.f)),
        ext_path = str(PurePath(args.u).joinpath("pagetext.xpi")),
      	show_browser = args.show_browser
    )
    links = []
    try:
    	links = scraper.scrapePages(pages)
    except Exception as e:
    	print(e)

    return links

with open(args.url_list, 'r') as f:
	url_list = [line.strip() for line in f]
	url_list.reverse()

pages_split = [url_list[i:i+args.n] for i in range(0, len(url_list), args.n)]

with Pool(args.n) as p:
	p.map(runScraperProcess, pages_split)
