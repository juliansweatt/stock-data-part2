#!/usr/bin/env python3

import sys
import requests
import re
from iex import Stock

class Tickers:
    """This is a test docstring"""

    # Ticker Settings
    NASDAQ_URL = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQrender=download"
    OUTFILE = "tickers.txt"
    PATTERN_SYMBOLS = re.compile(r'symbol/([a-z]*)')
    PATTERN_NEXT_PAGE = re.compile(r'<a href="(.{90,105})" id="main_content_lb_NextPage"')

    def print_to_file(self, outFile, tickerSet):
        """Prints a set to a file.

            Prints a set to an output file, such that each element of the
            set is a new line of the file.

            Args:
                outfile (str): The name/path of the output file.
                tickerSet (set): Set to print to the outfile
        """

        f = open(outFile, "w")
        for ticker in tickerSet:
            f.write(ticker + "\n")
        f.close()

    def get_tickers_from_url(self, url, maximum, currentTickers):
        """Gets stock tickers from a specified NASDAQ url.

            Function retrieves a maximum amount of tickers from a specified URL.
            A NASDAQ URL is expected. The maximum quantity takes in to account the current
            amount of tickers already found outside the function. The function will return whenever
            the maximum is reached or the page tickers are exhausted. The intent is to feed this 
            function each successive page URL. Depends upon the PATTERN_SYMBOLS global variable.

            Args:
                url (str): URL to retrieve stock data from.
                maximum (int): The maximum number of tickers to retrieve. 0 <= maximum <= 150.
                currentTickers: The current amount of tickers already retrieved.

            Returns:
                set: A set of tickers (str).
        """

        # Get Initial Web Page
        response = requests.get(url)

        # Harvest Tickers
        tickers = set(re.findall(self.PATTERN_SYMBOLS, response.text))

        # Check Tickers for Validity & Limit
        validTickers = set()
        for ticker in tickers:
            if len(validTickers)+currentTickers >= maximum:
                print(len(validTickers)+currentTickers,"Valid Ticker(s) Found. User Specified Limit Reached.")
                break
            try:
                Stock(ticker).price()
                validTickers.add(ticker)
            except:
                print("Invalid Ticker:", ticker)

        return validTickers

    def save_tickers(self, maximum):
        """Save a specified quantity of tickers to an output file.

            Saves a maximum number of tickers to an output file, such
            that each line in the output file is a ticker string.
            Depends upon the PATTERN_NEXT_PAGE global variable to set the
            pattern for finding the next page and the NASDAQ_URL global variable 
            for the first URL.

            Args:
                maximum (int): The maximum number of tickers to retrieve from NASDAQ.
        """
        # Initialize
        validTickers = set()
        currentURL = self.NASDAQ_URL

        while len(validTickers) < maximum:
            # Collect Tickers
            validTickers.update(self.get_tickers_from_url(currentURL,maximum,len(validTickers)))

            # Collect New Page URL
            response = requests.get(currentURL)
            currentURL = re.findall(self.PATTERN_NEXT_PAGE,response.text)[0]

            # Print Valid Ticker Set to Output File
            self.print_to_file(self.OUTFILE, validTickers)

            # Announce Page Change
            if len(validTickers) < maximum:
                print("Moving to Next Page", currentURL, "Valid Ticker(s) Found:", len(validTickers),)

if __name__ == '__main__':
    numTickers = int(sys.argv[1])
    t = Tickers()
    t.save_tickers(numTickers)