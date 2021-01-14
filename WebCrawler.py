# Web Crawler Date: 01-13-2021
# Author : Madhuri Gangadharan

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse ,urldefrag
import time
import collections

class Crawler:
    #Initialize the variables
    def __init__(self, start_url,maxpages):
        """
        @param start_url: The  start URL to crawl
        @param maxpages: maximum nuber of pages  to  crawl
        """
        self.domain = urlparse(start_url).netloc    #get the domain from the given url
        self.pool = ThreadPoolExecutor(max_workers=3)   # initialize a thread pool variable with maximum concurent threads to 3
        self.crawled = set([])  # contains the pages that is already visited
        self.to_crawl =collections.deque()  # queue of pages to be crawled
        self.to_crawl.append(start_url)
        self.pages = 0    # number of  child pages succesfully crawled so far
        self.totalpages = 0   # number of  pages succesfully crawled so far
        self.maxpages = maxpages   # maximum nuber of pages  to  crawl
        self.counter=0   # to check if the any pages are cralwed or not


    # url_in_list function is used to check if the URL is present in the list of URLs and avoid crawling same page as http or https
    def url_in_list(self,url, listobj):
        """
        @param url: url to check if its already existing in list
        @param listobj:  list of visited URLs
        """
        http_version = url.replace("https://", "http://")
        https_version = url.replace("http://", "https://")
        return (http_version in listobj) or (https_version in listobj)


    #checksamedomain function is used to check whether two netloc values are of same domain i.e within startpage's domain.
    def checksamedomain(self, netloc1, netloc2):
        """
        @param netloc1:  domain of current link
        @param netloc2:  domain of start page
        """
        domain1 = netloc1.lower()
        if "." in domain1:
            domain1 = domain1.split(".")[-2] + "." + domain1.split(".")[-1]

        domain2 = netloc2.lower()
        if "." in domain2:
            domain2 = domain2.split(".")[-2] + "." + domain2.split(".")[-1]

        return domain1 == domain2


    #parse_links function is used to parse the links and append it to the crawl queue
    def parse_links(self, html):
        """
        @param html: html text for the URL
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = [a.attrs.get("href") for a in soup.select("a[href]")]
        links = [urldefrag(link)[0] for link in links]    # remove fragment identifiers
        links = [
            link if bool(urlparse(link).netloc) else urljoin(self.crawl_url, link)    # if it's relative link, change to absolute
            for link in links
        ]
        if self.domain:
            links = [link for link in links if self.checksamedomain(urlparse(link).netloc, self.domain)]
        for link in links:
            if not self.url_in_list(link, self.crawled) and not self.url_in_list(link, self.to_crawl) and self.pages<self.maxpages:
                    self.counter=1
                    self.pages+=1
                    print("    "+link)
                    self.to_crawl.append(link)
        if self.counter == 0:
            print("    The children of this URL is already visited or the URL doesn't have any child")
        else:
            self.counter = 0


    # crawl_callback is a call back function  added to a thread pool executor
    def crawl_callback(self, res):
        """
        @param res: Response from the thread pool validate URL function
        """
        result = res.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)

    #validateURL function is used to check if its a valid URL and returns the response
    def validateURL(self, url):
        """
        @param url: URL to validate
        """
        try:
            res = requests.get(url)
            return res
        except requests.RequestException:
            print("Entered URL is invalid")
            return

   # run_crawler function uses thread mechanism to validate the URL and call the callback function
    def run_crawler(self):
        while self.totalpages < self.maxpages and self.to_crawl :
            try:
                self.crawl_url = self.to_crawl.popleft()
                if self.crawl_url not in self.crawled:
                    self.totalpages+=1
                    self.crawled.add(self.crawl_url)
                    print(self.crawl_url)
                    job = self.pool.submit(self.validateURL, self.crawl_url)  # used to submit the URLS to thread pool for execution
                    job.add_done_callback(self.crawl_callback) # Callback function in turn calls the parselink function
                time.sleep(2.5)
                self.pages = 0
            except Exception as e:
                print(e)
                continue


if  __name__ == '__main__':
    crawlurl = (input("Enter the  start URL to crawl ")).strip()
    obj = Crawler(crawlurl, 20)
    obj.run_crawler()