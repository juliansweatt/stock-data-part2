#!/usr/bin/env python3
import sys
import requests
import re
import argparse
import datetime
import os
import time
from iex import Stock

class Tickers:
    """Class used to save tickers to a file.

    :var str NASDAQ_URL: The National Association of Securities Dealers Automated Quotations URL to be crawled to retrieve tickers. - Default *http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQrender=download*
    :var str OUTFILE: File path to write tickers to. - Default: *tickers.txt*
    """

    # Ticker Settings
    def __init__(self):
        self.NASDAQ_URL = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQrender=download"
        self.OUTFILE = "tickers.txt"
        self._PATTERN_SYMBOLS_ = re.compile(r'symbol/([a-z]*)')
        self._PATTERN_NEXT_PAGE_ = re.compile(r'<a href="(.{90,105})" id="main_content_lb_NextPage"')

    def print_to_file(self, outFile, tickerSet):
        """Prints a set to a file.

            :Details: Prints a set to an output file, such that each element of the set is a new line of the file.
            :param int outfile: The name/path of the output file
            :param set tickerSet: Set to print to the outfile
        """

        f = open(outFile, "w")
        for ticker in tickerSet:
            f.write(ticker + "\n")
        f.close()

    def get_tickers_from_url(self, url, maximum, currentTickers):
        """Gets stock tickers from a specified NASDAQ url.

            :Details: Function retrieves a maximum amount of tickers from a specified URL. A *NASDAQ URL* is expected. The maximum quantity takes in to account the current amount of tickers already found outside the function. The function will return whenever the maximum is reached or the page tickers are exhausted. The intent is to feed this function each successive page URL.
            :param str url: URL to retrieve stock data from.
            :param maximum: The maximum number of tickers to retrieve.
            :type maximum: 0 <= int <= 110
            :param int currentTickers: The current amount of tickers already retrieved.
            :return: Retrieved tickers.
            :rtype: set of str
        """

        # Get Initial Web Page
        response = requests.get(url)

        # Harvest Tickers
        tickers = set(re.findall(self._PATTERN_SYMBOLS_, response.text))

        # Check Tickers for Validity & Limit
        validTickers = set()
        for ticker in tickers:
            if len(validTickers)+currentTickers >= maximum:
                print(len(validTickers)+currentTickers,"Valid Ticker(s) Found. User Specified Limit Reached.")
                break
            try:
                Stock(ticker).price()
                validTickers.add(ticker.upper())
            except:
                print("Invalid Ticker:", ticker)

        return validTickers

    def save_tickers(self, maximum):
        """Save a specified quantity of tickers to an output file.

        :Details: Saves a maximum number of tickers to an output file, suchthat each line in the output file is a ticker string.
        :param int maximum: The maximum number of tickers to retrieve from NASDAQ.
        """
        # Initialize
        validTickers = set()
        currentURL = self.NASDAQ_URL

        while len(validTickers) < maximum:
            # Collect Tickers
            validTickers.update(self.get_tickers_from_url(currentURL,maximum,len(validTickers)))

            # Collect New Page URL
            response = requests.get(currentURL)
            currentURL = re.findall(self._PATTERN_NEXT_PAGE_,response.text)[0]

            # Print Valid Ticker Set to Output File
            self.print_to_file(self.OUTFILE, validTickers)

            # Announce Page Change
            if len(validTickers) < maximum:
                print("Moving to Next Page", currentURL, "Valid Ticker(s) Found:", len(validTickers),)

class Fetcher:
    """...
    """

    # Ticker Settings
    def __init__(self, tfile="tickers.txt", ifile="default_out.txt"):
        # Do something
        self.tickerFile = tfile
        self.infoFile = ifile

    def getTickers(self):
        """Retrieve a set of tickers from a text file.

            :Details: Retrieves a set of tickers from the tickerFile which is a text file such that each line of the text file is a new ticker represented as a string.
            :return: Valid tickers.
            :rtype: set
        """
        tickers = set()

        try:
            f = open(self.tickerFile, "r") # Bookmark
            for line in f:
                tickers.add(line[:-1])
            f.close()
        except:
            print("Error While Accessing the Ticker File.") # @todo Make exception
            return

        return tickers

    def makeTimeString(self, hour, minute):
        """Makes a time string (HH:MM) from hour and minute.

        :param int hour: The hour of the time.
        :param int minute: The minute of the time.
        :return: Time in the form HH:MM, substituting 0 as needed.
        :rtype: str
        """

        timeString = str()
        hourString = str()
        minuteString = str()

        if hour < 10:
            hourString = "0" + str(hour)
        else:
            hourString = str(hour)

        if minute < 10:
            minuteString = "0" + str(minute)
        else:
            minuteString = str(minute)
        
        timeString = hourString + ":" + minuteString

        return timeString

    def fetch(self, timeLimit):
        # Collect Stock Tickers
        tickerSet = self.getTickers()

        # Setup for Print File
        exists = os.path.isfile(self.infoFile)
        outfile = open(self.infoFile, "a")
        if not exists:
            # Initialize File if New
            outfile.write("Time,Ticker,latestPrice,latestVolume,Close,Open,low,high\n")
        outfile.flush()

        # Timed Execution
        endTime = time.time() + timeLimit
        currentMinute = datetime.datetime.now().minute
        firstPass = True
        while time.time() < endTime:
            if firstPass or (datetime.datetime.now().minute != currentMinute):
                # 
                if not exists and firstPass:
                    print("Retrieving Stock Data")
                    firstPass = False
                else:
                    print("Updating Stock Data at", datetime.datetime.now().time())

                # Execute Update Here
                for ticker in tickerSet:
                    tickInfo = Stock(ticker).quote()
                    tickStr = str(self.makeTimeString(datetime.datetime.now().hour, datetime.datetime.now().minute) + "," + ticker + "," + str(tickInfo["latestPrice"]) + ",")
                    tickStr = tickStr + str(tickInfo["latestVolume"]) + "," + str(tickInfo["close"]) + "," + str(tickInfo["open"]) + ","
                    tickStr = tickStr + str(tickInfo["low"]) + "," + str(tickInfo["high"]) + "\n"
                    outfile.write(tickStr)
                currentMinute = datetime.datetime.now().minute
                outfile.flush()
        print("Time Limit Has Expired at", datetime.datetime.now().time())
        outfile.close()
