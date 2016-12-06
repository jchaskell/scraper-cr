"""Scrapes Senate congressional record. Input is: directory where to print the files start date: 01-01-2000 format, end date. End date defaults to current date if none given"""

import os, re, random, codecs, sys, requests, time
from datetime import datetime, date, timedelta as td
from bs4 import BeautifulSoup
from time import sleep
# import filterCR #this will have functions (or a class?) to take CR and put it into files per person per congress
# import datetime as dt #change script later to use this

class scrapeCR:

    def __init__(self, start_date, end_date, directory):
        ####Change self.pause for amount you want to pause between calls to the website(it randomizes between 0 sec and the your input)
        self.pause  = 4

        self.url_beg = "https://www.congress.gov/congressional-record/"
        self.url_end = "/senate-section"

        self.start_date = start_date
        self.end_date = end_date
        self.directory = directory

    def daterange(self, start_date, end_date):
        """Creates a generator over a list of dates between the start and end date"""
        #borrowed from: http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
        for n in range(int ((end_date - start_date).days)):
            yield start_date + td(n)

    def scrape(self):
        """Defines and runs through scraping loops"""
        #create a list  of all of the dates
        dates_to_scrape = [single_date.strftime("%Y/%m/%d") for single_date in self.daterange(self.start_date, self.end_date)]

        os.chdir(self.directory)
        for date in dates_to_scrape:
            # print date
            #get url
            main_url = self.url_beg + date + self.url_end
            filename = re.sub("/", "_", date) + ".txt"
            #test url for page without links
            links = self.get_links(main_url)
            if len(links) == 0:
                continue
            sleep(random.uniform(0,self.pause))
            dailyCR = ""
            for l in links:
                if re.match("^/", l): #links used to be full links, now truncated
                    link_fix = "https://www.congress.gov" + l
                else:
                    link_fix = l
                text = self.scrape_page(link_fix)
                dailyCR += " " + text

            #print to file
            with open(filename, "w") as file:
                file.write(dailyCR)

    def get_links(self, url):
        """Gets links for one day of Senate CR"""
        # print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        tds = [td for td in soup.find_all('td')] #only even numbered indexes
        tds_relevant = [tds[i] for i in range(len(tds)) if i % 2 == 0]
        links = [link.a.get('href') for link in tds_relevant]
        return(links)

    def scrape_page(self, url):
        """Scrapes one page from the CR and outputs it to a file"""
        # print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        try: #sometimes I get an attribute error that doesn't seem to be real (it doesn't happen every time when I run the same code again), so I try 10 times with a pause
            text = soup.find('pre', class_ = 'styled').contents
            text_all = ''.join(unicode(text))
            return text_all
        except AttributeError:
            test = 0
            while test < 10: #I have no had a problem with this breaking but it feasibly could
                sleep(random.uniform(0,self.pause))
                try:
                    text = soup.find('pre', class_ = 'styled').contents
                    text_all = ''.join(unicode(text))
                    return text_all
                except AttributeError:
                    test += 1

def main(args):
    """Initializes class and runs through the functions"""
    directory = args[0]

    #create dates
    start_date = args[1].split("-")
    start_date = date(int(start_date[2]), int(start_date[0]), int(start_date[1]))
    if len(args) == 3:
        end_date = args[2].split("-")
    else:
        end_date = time.strftime("%d-%m-%Y").split("-")
    end_date =date(int(end_date[2]), int(end_date[0]), int(end_date[1]))
    scrape = scrapeCR(start_date, end_date, directory)
    scrape.scrape()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Too few arguments")
        sys.exit()
    else:
        args = sys.argv[1:]
        main(args)



