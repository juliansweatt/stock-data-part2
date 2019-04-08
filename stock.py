#!/usr/bin/env python3
import sys
import requests
import re
import argparse
from iex import Stock

class Tickers:
    """Class used to save tickers to a file."""

    # Ticker Settings
    def __init__(self):
        self.NASDAQ_URL = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQrender=download"
        self.OUTFILE = "tickers.txt"
        self.PATTERN_SYMBOLS = re.compile(r'symbol/([a-z]*)')
        self.PATTERN_NEXT_PAGE = re.compile(r'<a href="(.{90,105})" id="main_content_lb_NextPage"')

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
                maximum (int): The maximum number of tickers to retrieve. 0 <= maximum <= 110.
                currentTickers(int): The current amount of tickers already retrieved.

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

def int_in_range(i):
    """Argument filter for an integer between 0 and 110.

    Args:
        i (int): The integer to filter.

    Returns:
        (int) Returns the number as an integer if within range, throws an error otherwise.
    """
    inti = int(i)
    if inti < 0 or inti > 110:
        raise argparse.ArgumentTypeError("0 < ticker_count <= 110 is not satisfied by %d" % i)
    return inti

def parseInput():
    """Parse arguments from standard input.

    Returns:
        Returns arguments object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", type=str, choices=("Ticker","Fetcher","Query"), help="Operation to perform.", required=True)
    parser.add_argument("--ticker_count", type=int_in_range, help="Number of Tickers to Retrieve (0 < ticker_count <= 110)", required=(parser.parse_known_args()[0].operation in ("Ticker","Fetcher")))
    return parser.parse_args()

if __name__ == '__main__':
    # Parse Input
    args = parseInput()

    # Execute Cooresponding Operation
    if args.operation == "Ticker":
        Tickers().save_tickers(args.ticker_count)